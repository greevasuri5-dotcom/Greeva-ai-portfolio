import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title = "Inventory & reorder assistant", layout = "wide")
st.title("inventory & reorder assistant(suri sons)")
st.caption("upload sales data to see KPIs, charts, and reorder suggestons. Optionally upload current stock to compute final order quantities.")

with st.expander("required csv formats"), exapanded=False:
  st.markdown(""" sales.csv columns: - date, item, name, category, size, quantity sold, price
  current_stock.csv(optional) columns: - item name, category, size, quantity in stock """)

sales_file = st.file_uploader("upload sales.csv", type = ["csv"])
stock_file = st.file_uploader("upload current_stock.csv (optional)", type = ["csv"])

st.sidebar.header("settings")
lookback_days = st.sidebar.slider("moving average look-back (days)", min_value = 3, max_value=30,value=7, step=1)
top_n = st.sidebar.slider("top items to display", min_value=5, max_value=20, value=10, step=1)

def clean_sales_df(df: pd.DataFrame)
pd.DataFrame:
  required_cols = ["date", "item name", "category", "size", "quantity sold", "price"]
  missing = [c for c in required_cols if c not in df.columns]
    if missing:
      st.error(f"missing columns in sales.csv: {missing}")
      return pd.DataFrame()

  df = df.copy()
  df["date"] = pd.to_datetime(df["Date"], errors = "coerce")
  for col in ["quantity sold", "price"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["revenue"] = df["quantity sold"] * df["price"]
    return df


                            
