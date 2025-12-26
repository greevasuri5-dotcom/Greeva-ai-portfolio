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

def clean_stock_df (de:pd.DataFrame) pd.DataFrame:
  required_cols = ["item name", "category", "size", "quantity in stock"]
  missing = [c for c in required_cols if c not in df.columns]
  if missing:
    st.warning (f"missing column in current_stock.csv:{missing}")
    return pd.DataFrame()
  df = df.copy()
  df["quantity in stock"] = pd.to_numeric (df["quantity in stock"], errors = "coerce").fillna(0)
  return df

if sales_file is not None:
  sales_df_raw = pd.read_csv(sales_file)
  sales_df = clean_sales_df (sales_df_raw)
  
  if sales_df.empty:
    st.stop()

  st.subheader ("sales preview")
  st.dataframe(sales_df.head(20), use_container_width = true)


  total_rev = int (sales_df["revenue"].sum())
  total_qty = int (sales_df["quantity sold"].sum())
  unique_items = sales_df["item name"].nunique()
  col1, col2, col3 = st.columns(3)
  col1.metric("total revenue (rs)", f"{total_rev}")
  col2.metric("units sold", f"{total_qty:,}")
  col3.metric("unique items", f"{unique items:, }")


  st.subheader("filters")
  categories = ["(all)"] + sorted (sales_df ["category"].dropna().unique().tolist())
  chosen_cat = st.selectbox("filter by category", categories, index = 0)
  filtered = sales_df if chosen cat == "(all)"
  else sales_df [sales_df["category"] == chosen_cat]

  st.subheader("top items by quantity")
  top_items = filtered.groupby("item name") ["quanity sold"].sum().sort_values(ascending = False).head(top_n)
  st.bar_chart(top_items)

  st.subheader("daily revenue")
  daily = filtered.dropna(subset = ["date"]).groupby("date") ["revenue"].sum()
  st.line_chart(daily)

  st.subheader("reorder suggestions")
  daily_item = filtered.groupby(["item name", "date"])["quantity sold"].sum().reset_index("date")
  
  reorder_rows = []
  for item, g in daily_item.groupby("item name"):
    g = g.sort_values("date").set_index("date")
    if g.index.size == 0:
      suggestions = 0
    else:
      full_index = pd.date_range(g.index.min(),g.index.max(), freq = "d")
      g = g.reindex(full_index).fillna(0)
      g["ma"] = g["quanity sold"].rolling(lookback_days).mean()
      suggestions = int(np.ceil(g["ma"].iloc[-1])) if not g["ma"].isna().all() else 0

      reorder_rows.append({"item name": item,"suggested reorder qty" : suggestions})
      reorder_df = pd.dataframe(reorder_rows).sort_values("suggested reorder qty", ascending = False)

      cat_map = filtered.set_index("item name") ["category"].to_dict()
      size_map = filtered.set_index("item name") ["size"].to_dict()
      reorder_df["category"] = reorder_df ["item name"].map(cat_map)
      reorder_df["size (last sold)"] = reorder_df["item name"].map(size_map)

      if stock_file is not None:
        stock_df_raw = pd.read_csv(stock_file)
        stock_df = clean_stock_df(stock_df_raw)
        if not tock_df.empty:
          stock_by_item = stock_df.groupby("item name")["quanity in stock"].sum()
          reorder_df ["current stock (sum)"] = reorder_df["item name"].map(stock_by_item).fillna(0).astype(int)
          reorder_df["final order qty"] = (reorder_df ["suggested reorder qty"] - reorder_df["current stock(sum)"]).clip(lower = 0).astype(int)
          st.dataframe(reorder_df, use_container_width = True)
        else:  
          st.dataframe(reorder_df, use_container_width = True)

        filename = "supplier_order.csv" if stock_file is not None else "reorder_suggestions.csv"
        csv_bytes = reorder_df.to_csv(index = False).encode("utf-8")
        st.download_button("download csv, data = csv_bytes, file_name = filename, mime = "text/csv")
        with st.expander("notes", expanded = False):
           st.markdown(f""" - reorder suggestion uses a {lookback_days}-day moving average.
                            - upload current_stock.csv to compute Final order qty.
                            - improve accuracy by feeding more recent and seasonal data.

        else:
           st.info("upload sales.csv to see KPIs, charts, reorder suggestions.")

                      
