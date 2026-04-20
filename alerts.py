from inventory import get_all_items_df
from forecasting import forecast_depletion

def check_alerts():
    df = get_all_items_df()
    alerts = []
    
    for _, item in df.iterrows():
        # Check low stock alert
        if item['current_quantity'] <= item['reorder_point']:
            alerts.append(f"⚠️ LOW STOCK: {item['name']} has only {item['current_quantity']} left (Reorder point: {item['reorder_point']})")
        
        # Check forecast alert
        forecast = forecast_depletion(item['id'])
        if 'error' not in forecast:
            days = forecast['days_until_stockout']
            lead_time = item['lead_time_days']
            if days <= lead_time:
                alerts.append(f"📉 PREDICTED STOCKOUT: {item['name']} will run out in {days} days (Lead time: {lead_time} days)")
    
    return alerts