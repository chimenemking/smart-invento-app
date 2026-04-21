import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory import add_item, record_sale, record_purchase, delete_item, get_all_items_df, get_sales_history

def test_add_item_blackbox(test_db):
    """Black-box: Add item and verify output without knowing internals"""
    # Use the test_db fixture to get a session
    from database import get_session
    session = test_db
    
    # Override get_session to use test_db
    import inventory
    original_get_session = inventory.get_session
    inventory.get_session = lambda: session
    
    try:
        item_id = add_item("Test Laptop", 100.0, 25.0, 7)
        df = get_all_items_df()
        assert len(df) == 1
        assert df.iloc[0]['name'] == "Test Laptop"
        assert df.iloc[0]['current_quantity'] == 100.0
    finally:
        inventory.get_session = original_get_session


def test_record_sale_blackbox(test_db):
    """Black-box: Record sale and verify stock decreases"""
    from database import get_session
    session = test_db
    
    import inventory
    original_get_session = inventory.get_session
    inventory.get_session = lambda: session
    
    try:
        item_id = add_item("Test Mouse", 50.0)
        record_sale(item_id, 10.0)
        df = get_all_items_df()
        assert df.iloc[0]['current_quantity'] == 40.0
    finally:
        inventory.get_session = original_get_session


def test_record_purchase_blackbox(test_db):
    """Black-box: Record purchase and verify stock increases"""
    from database import get_session
    session = test_db
    
    import inventory
    original_get_session = inventory.get_session
    inventory.get_session = lambda: session
    
    try:
        item_id = add_item("Test Keyboard", 50.0)
        record_purchase(item_id, 20.0)
        df = get_all_items_df()
        assert df.iloc[0]['current_quantity'] == 70.0
    finally:
        inventory.get_session = original_get_session


def test_delete_item_blackbox(test_db):
    """Black-box: Delete item and verify it's gone"""
    from database import get_session
    session = test_db
    
    import inventory
    original_get_session = inventory.get_session
    inventory.get_session = lambda: session
    
    try:
        item_id = add_item("Test Delete", 100.0)
        df_before = get_all_items_df()
        assert len(df_before) == 1
        
        delete_item(item_id)
        df_after = get_all_items_df()
        assert len(df_after) == 0
    finally:
        inventory.get_session = original_get_session