import streamlit as st
from inventory import get_all_items_df
from forecasting import forecast_depletion

st.title("Test")

df = get_all_items_df()
item_name = st.selectbox("Item", df['name'].tolist())
item_id = int(df[df['name'] == item_name]['id'].iloc[0])  # Convert to int

st.write(f"Item ID: {item_id} (type: {type(item_id)})")

result = forecast_depletion(item_id)
st.write(result)