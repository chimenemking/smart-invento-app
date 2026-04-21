import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np
from datetime import datetime, timedelta

def test_stress_large_dataset(test_db):
    """Stress test: 100 items with 365 days history each"""
    from database import get_session
    from inventory import add_item, record_sale, get_all_items_df, get_sales_history
    from forecasting import forecast_depletion
    
    session = test_db
    import inventory
    original_get_session = inventory.get_session
    inventory.get_session = lambda: session
    
    try:
        start_time = time.time()
        
        # Create 100 items
        item_ids = []
        for i in range(100):
            name = f"Stress Item {i}"
            item_id = add_item(name, 500.0, 50.0, 7)
            item_ids.append(item_id)
        
        # Add 365 days of random sales for first 10 items
        for item_id in item_ids[:10]:
            for day in range(365):
                sale_date = datetime.now().date() - timedelta(days=364-day)
                qty = np.random.randint(5, 30)
                record_sale(item_id, qty, sale_date)
        
        load_time = time.time() - start_time
        print(f"Created 100 items + 3650 sales records in {load_time:.2f} seconds")
        
        # Should complete in reasonable time
        assert load_time < 30.0
        
        # Test dashboard load
        df_start = time.time()
        df = get_all_items_df()
        df_time = time.time() - df_start
        assert len(df) == 100
        assert df_time < 2.0
        
        # Test forecast on one item
        forecast_start = time.time()
        pred = forecast_depletion(item_ids[0])
        forecast_time = time.time() - forecast_start
        assert "error" not in pred
        assert forecast_time < 5.0
        
    finally:
        inventory.get_session = original_get_session