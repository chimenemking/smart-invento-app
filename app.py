import streamlit as st
import pandas as pd
import plotly.express as px
from inventory import add_item, record_sale, record_purchase, get_all_items_df, delete_item, get_sales_history
from forecasting import forecast_depletion, get_daily_demand_history
from alerts import check_alerts

st.set_page_config(page_title="Smart Inventory", layout="wide")
st.title("📦 Smart Inventory Monitoring & Forecasting")

# Sidebar
page = st.sidebar.selectbox("Menu", ["Dashboard", "Manage Items", "Record Transaction", "Forecast & Trends", "Alerts"])

# Dashboard
if page == "Dashboard":
    st.header("Current Inventory")
    df = get_all_items_df()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Stock status chart
        fig = px.bar(df, x='name', y='current_quantity', color='current_quantity',
                     title="Stock Levels", labels={'current_quantity': 'Quantity'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No items yet. Add items in 'Manage Items' page.")

# Manage Items
elif page == "Manage Items":
    st.header("Add New Item")
    with st.form("add_item"):
        name = st.text_input("Item Name")
        qty = st.number_input("Initial Quantity", min_value=0.0, step=1.0)
        reorder = st.number_input("Reorder Point", min_value=0.0, step=1.0, value=10.0)
        lead_time = st.number_input("Lead Time (days)", min_value=1, step=1, value=7)
        submitted = st.form_submit_button("Add Item")
        if submitted and name:
            add_item(name, qty, reorder, lead_time)
            st.success(f"Added {name}")
            st.rerun()
    
    st.header("Delete Item")
    df = get_all_items_df()
    if not df.empty:
        item_to_delete = st.selectbox("Select item to delete", df['name'].tolist())
        if st.button("Delete"):
            item_id = df[df['name'] == item_to_delete]['id'].iloc[0]
            delete_item(item_id)
            st.success(f"Deleted {item_to_delete}")
            st.rerun()

# Record Transaction
elif page == "Record Transaction":
    st.header("Record Sale or Purchase")
    df = get_all_items_df()
    if not df.empty:
        item_name = st.selectbox("Item", df['name'].tolist())
        item_id = int(df[df['name'] == item_name]['id'].iloc[0])
        
        transaction_type = st.radio("Type", ["Sale", "Purchase"])
        qty = st.number_input("Quantity", min_value=0.01, step=1.0)
        
        if st.button("Record"):
            if transaction_type == "Sale":
                record_sale(item_id, qty)
                st.success(f"Recorded sale of {qty} {item_name}")
            else:
                record_purchase(item_id, qty)
                st.success(f"Recorded purchase of {qty} {item_name}")
            st.rerun()
    else:
        st.warning("No items available")

# Forecast & Trends
elif page == "Forecast & Trends":
    st.header("Forecast & Demand Trends")
    df = get_all_items_df()
    if not df.empty:
        item_name = st.selectbox("Select item", df['name'].tolist(), key="forecast_select")
        item_id = int(df[df['name'] == item_name]['id'].iloc[0])
        
        forecast_result = forecast_depletion(item_id)
        
        if 'error' in forecast_result:
            st.error(forecast_result['error'])
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Predicted Daily Demand", f"{forecast_result['predicted_daily_demand']} units/day")
            with col2:
                st.metric("Days Until Stockout", f"{forecast_result['days_until_stockout']} days")
            
            # Historical demand chart
            history = get_daily_demand_history(item_id)
            if not history.empty:
                fig = px.line(x=history.index, y=history.values, 
                             title=f"Daily Sales History - {item_name}",
                             labels={'x': 'Date', 'y': 'Units Sold'})
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No items available")

# Alerts
elif page == "Alerts":
    st.header("Active Alerts")
    alerts = check_alerts()
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("No active alerts - all stock levels are healthy!")