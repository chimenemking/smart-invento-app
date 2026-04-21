from inventory import get_all_items_df, get_sales_history
import pandas as pd

print("=== ALL ITEMS IN INVENTORY ===\n")
df_items = get_all_items_df()
print(df_items.to_string())
print(f"\nTotal items: {len(df_items)}")

print("\n" + "="*50)
print("=== SALES HISTORY FOR EACH ITEM ===\n")

for _, item in df_items.iterrows():
    item_id = item['id']
    item_name = item['name']
    df_sales = get_sales_history(item_id)
    
    if df_sales.empty:
        print(f"📦 {item_name}: No sales recorded yet")
    else:
        print(f"📊 {item_name}: {len(df_sales)} sales records")
        print(df_sales.tail(5))  # Show last 5 sales
        print(f"   Total units sold: {df_sales['quantity_sold'].abs().sum()}")
    print("-" * 40)

# Check Test Product specifically
print("\n" + "="*50)
print("=== FORECAST READINESS ===\n")

for _, item in df_items.iterrows():
    item_name = item['name']
    df_sales = get_sales_history(item['id'])
    
    if len(df_sales) >= 7:
        print(f"✅ {item_name}: Ready for forecasting ({len(df_sales)} days of data)")
    elif len(df_sales) > 0:
        print(f"⚠️ {item_name}: Needs {7 - len(df_sales)} more days of sales for forecast")
    else:
        print(f"❌ {item_name}: No sales data. Record some sales first.")