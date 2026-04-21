from database import get_session, Item

session = get_session()
items = session.query(Item).all()

for item in items:
    # Set reasonable stock levels
    if item.name == "Test Product":
        item.current_quantity = 500
    elif item.name in ["Tomato", "Pepper", "Pineapple", "Cucumber", "Carrot", "Lettuce", "Spinach", "Broccoli", "Celery", "Eggplant"]:
        item.current_quantity = 100
    else:
        item.current_quantity = 50
    
    print(f"{item.name}: {item.current_quantity}")

session.commit()
session.close()
print("\n✅ Stock levels reset to positive values")