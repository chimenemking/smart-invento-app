from inventory import add_item, record_sale, get_all_items_df, get_sales_history
from datetime import datetime, timedelta
import random

# ===========================================
# 10 NEW ITEMS (never existed before)
# ===========================================
NEW_ITEMS = [
    ("Tomato", 100, 15, 5),
    ("Pepper", 80, 12, 4),
    ("Pineapple", 60, 10, 7),
    ("Cucumber", 90, 14, 4),
    ("Carrot", 120, 20, 6),
    ("Lettuce", 70, 10, 3),
    ("Spinach", 50, 8, 4),
    ("Broccoli", 85, 12, 5),
    ("Celery", 75, 10, 4),
    ("Eggplant", 65, 10, 5),
]

print("=" * 60)
print("STEP 1: Adding 10 new items")
print("=" * 60)

for name, qty, reorder, lead in NEW_ITEMS:
    try:
        add_item(name, initial_qty=qty, reorder_point=reorder, lead_time=lead)
        print(f"✅ Added {name} (Stock: {qty}, Reorder: {reorder})")
    except Exception as e:
        print(f"⚠️ {name} might already exist: {e}")

print("\n" + "=" * 60)
print("STEP 2: Adding 30 days of sales for ALL items")
print("=" * 60)

# Get all items (existing + new)
df = get_all_items_df()

for _, item in df.iterrows():
    item_id = item['id']
    item_name = item['name']
    
    # Check existing sales
    existing = len(get_sales_history(item_id))
    
    if existing >= 30:
        print(f"⏭️ {item_name}: Already has {existing} records (skipping)")
        continue
    
    print(f"\n📦 Adding 30 days of sales for: {item_name}")
    
    for i in range(30):
        sale_date = datetime.now().date() - timedelta(days=29 - i)
        qty_sold = random.randint(5, 25)
        record_sale(item_id, qty_sold, sale_date)
    
    print(f"   ✅ Done for {item_name}")

print("\n" + "=" * 60)
print("FINAL VERIFICATION")
print("=" * 60)

df_final = get_all_items_df()
print(f"\nTotal items in database: {len(df_final)}\n")

for _, item in df_final.iterrows():
    count = len(get_sales_history(item['id']))
    status = "✅" if count >= 30 else "⚠️" if count > 0 else "❌"
    print(f"{status} {item['name']}: {count} sales records | Stock: {item['current_quantity']}")

print("\n" + "=" * 60)
print("🎯 Complete! Now run: streamlit run app.py")
print("   Then go to Forecast & Trends page")
print("=" * 60)