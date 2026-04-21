from database import get_session, SalesHistory

session = get_session()
count = session.query(SalesHistory).count()
print(f"Total sales records in database: {count}")

if count > 0:
    print("\nFirst 5 records:")
    for sale in session.query(SalesHistory).limit(5):
        print(f"  Item ID: {sale.item_id}, Date: {sale.date}, Qty: {sale.quantity_sold}")
else:
    print("\n❌ No sales records found!")

session.close()