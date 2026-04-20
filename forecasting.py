import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from datetime import datetime, timedelta
from inventory import get_all_items_df, get_sales_history

def get_daily_demand_history(item_id):
    df = get_sales_history(item_id)
    if df.empty:
        return pd.Series([])
    
    # Filter only sales (negative quantity_sold means sale)
    sales_df = df[df['quantity_sold'] < 0].copy()
    sales_df['quantity_sold'] = sales_df['quantity_sold'].abs()
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    
    # Aggregate by day
    daily = sales_df.groupby('date')['quantity_sold'].sum()
    return daily

def forecast_depletion(item_id, forecast_days=30):
    session = None  # Not needed with current functions
    history = get_daily_demand_history(item_id)
    
    if len(history) < 7:
        return {"error": "Insufficient history (need at least 7 days of data)"}
    
    # Get current quantity
    df = get_all_items_df()
    item = df[df['id'] == item_id]
    if item.empty:
        return {"error": "Item not found"}
    
    current_qty = item.iloc[0]['current_quantity']
    
    # Exponential Smoothing
    try:
        model = SimpleExpSmoothing(history).fit(smoothing_level=0.3, optimized=True)
        forecast = model.forecast(forecast_days)
        daily_demand = max(forecast.mean(), 0.01)  # Avoid division by zero
    except:
        # Fallback to simple average
        daily_demand = max(history.mean(), 0.01)
        forecast = pd.Series([daily_demand] * forecast_days)
    
    days_to_depletion = current_qty / daily_demand if daily_demand > 0 else float('inf')
    
    return {
        "predicted_daily_demand": round(float(daily_demand), 2),
        "days_until_stockout": round(days_to_depletion, 1),
        "forecast_dates": [(datetime.now() + timedelta(days=i)).date() for i in range(forecast_days)],
        "forecast_values": forecast.tolist(),
        "model_used": "Exponential Smoothing"
    }