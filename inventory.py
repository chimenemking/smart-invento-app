from database import get_session, Item, SalesHistory
import pandas as pd
from datetime import date

def add_item(name, initial_qty=0, reorder_point=10, lead_time=7):
    session = get_session()
    item = Item(name=name, current_quantity=initial_qty, 
                reorder_point=reorder_point, lead_time_days=lead_time)
    session.add(item)
    session.commit()
    item_id = item.id
    session.close()
    return item_id

def update_stock(item_id, delta_qty, reason="sale", transaction_date=None):
    if transaction_date is None:
        transaction_date = date.today()
    
    session = get_session()
    item = session.query(Item).filter(Item.id == item_id).first()
    if item:
        item.current_quantity += delta_qty
        # Log to sales history (negative for sales, positive for purchases)
        qty_log = -delta_qty if reason == "sale" else delta_qty
        history_record = SalesHistory(
            item_id=item_id, 
            date=transaction_date, 
            quantity_sold=qty_log
        )
        session.add(history_record)
        session.commit()
    session.close()

def record_sale(item_id, qty, sale_date=None):
    update_stock(item_id, -qty, reason="sale", transaction_date=sale_date)

def record_purchase(item_id, qty, purchase_date=None):
    update_stock(item_id, qty, reason="purchase", transaction_date=purchase_date)

def get_all_items_df():
    session = get_session()
    items = session.query(Item).all()
    df = pd.DataFrame([{
        'id': i.id, 
        'name': i.name, 
        'current_quantity': i.current_quantity,
        'reorder_point': i.reorder_point,
        'lead_time_days': i.lead_time_days
    } for i in items])
    session.close()
    return df

def delete_item(item_id):
    session = get_session()
    session.query(SalesHistory).filter(SalesHistory.item_id == item_id).delete()
    session.query(Item).filter(Item.id == item_id).delete()
    session.commit()
    session.close()

def get_sales_history(item_id):
    session = get_session()
    sales = session.query(SalesHistory).filter(SalesHistory.item_id == item_id).all()
    df = pd.DataFrame([{'date': s.date, 'quantity_sold': s.quantity_sold} for s in sales])
    session.close()
    return df