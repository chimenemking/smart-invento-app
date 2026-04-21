import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_forecast_whitebox_insufficient_data(test_db):
    """White-box: Test error handling for insufficient history"""
    from database import get_session
    from inventory import add_item
    from forecasting import forecast_depletion
    
    session = test_db
    import inventory
    original_get_session = inventory.get_session
    inventory.get_session = lambda: session
    
    try:
        item_id = add_item("Test Item", 100.0)
        result = forecast_depletion(item_id)
        assert "error" in result
    finally:
        inventory.get_session = original_get_session


def test_forecast_whitebox_with_data(test_db):
    """White-box: Test forecast with known data"""
    from database import get_session
    from inventory import add_item, record_sale
    from forecasting import forecast_depletion
    
    session = test_db
    import inventory
    original_get_session = inventory.get_session
    inventory.get_session = lambda: session
    
    try:
        item_id = add_item("Constant Item", 200.0)
        
        # Add 30 days of constant sales (10 units per day)
        for i in range(30):
            sale_date = datetime.now().date() - timedelta(days=29-i)
            record_sale(item_id, 10.0, sale_date)
        
        result = forecast_depletion(item_id)
        
        # Check that we don't have an error
        assert "error" not in result, f"Got error: {result.get('error')}"
        
        # Should be close to 10 (allow some variation)
        assert result["predicted_daily_demand"] > 8
        assert result["predicted_daily_demand"] < 12
        
    finally:
        inventory.get_session = original_get_session


def test_forecast_validation_accuracy(test_db):
    """Validation testing: Train/test split with MAE/RMSE"""
    from database import get_session
    from inventory import add_item, record_sale
    from statsmodels.tsa.holtwinters import SimpleExpSmoothing
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    
    session = test_db
    import inventory
    original_get_session = inventory.get_session
    inventory.get_session = lambda: session
    
    try:
        item_id = add_item("Validation Item", 500.0)
        
        # Generate 60 days of sales with pattern
        np.random.seed(42)
        for i in range(60):
            sale_date = datetime.now().date() - timedelta(days=59-i)
            qty = 15 + np.random.normal(0, 3)
            record_sale(item_id, max(1, qty), sale_date)
        
        # Get sales history
        from inventory import get_sales_history
        df = get_sales_history(item_id)
        df['date'] = pd.to_datetime(df['date'])
        daily = df.groupby('date')['quantity_sold'].sum()
        
        # Need at least 10 days for test
        if len(daily) < 20:
            pytest.skip("Not enough data generated")
        
        # Train/test split (last 10 days for test)
        train = daily.iloc[:-10]
        test = daily.iloc[-10:]
        
        # Fit model
        model = SimpleExpSmoothing(train).fit(optimized=True)
        forecast = model.forecast(10)
        
        mae = mean_absolute_error(test, forecast)
        rmse = np.sqrt(mean_squared_error(test, forecast))
        
        # Acceptable thresholds
        assert mae < 10.0
        assert rmse < 12.0
        
    finally:
        inventory.get_session = original_get_session