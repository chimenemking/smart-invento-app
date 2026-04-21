import streamlit as st
from inventory import get_all_items_df
from forecasting import forecast_depletion

df = get_all_items_df()
st.write(df)

item_id = 7  # Tomato
result = forecast_depletion(item_id)
st.write(result)