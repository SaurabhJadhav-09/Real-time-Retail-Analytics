"""
dashboard.py

Real-Time Retail Analytics Dashboard — reads the live order feed that
simulate_orders.py is writing into DynamoDB, and redraws every few seconds.

Run on the EC2 instance with:
    streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0

Then visit http://<ec2_public_ip>:8501
"""

import os
import time
from datetime import datetime

import boto3
import pandas as pd
import plotly.express as px
import streamlit as st

AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "retail_live_orders")

st.set_page_config(
    page_title="Real-Time Retail Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- Data loading ----------------
def fetch_all_orders() -> pd.DataFrame:
    """Scan the whole DynamoDB table. Fine for a demo-scale table
    (thousands of rows); for a production system you'd page/query instead."""
    session = boto3.Session(region_name=AWS_REGION)
    table = session.resource("dynamodb").Table(DYNAMODB_TABLE)

    items = []
    response = table.scan()
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    if not items:
        return pd.DataFrame()

    df = pd.DataFrame(items)
    numeric_cols = ["units_sold", "unit_price", "unit_cost", "total_revenue", "total_cost", "total_profit"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "order_date" in df.columns:
        df["order_date_parsed"] = pd.to_datetime(df["order_date"], errors="coerce")
    if "ingested_at" in df.columns:
        df["ingested_at_parsed"] = pd.to_datetime(df["ingested_at"], errors="coerce")

    return df


# ---------------- Sidebar controls ----------------
st.sidebar.title("Dashboard Controls")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
refresh_seconds = st.sidebar.slider("Refresh interval (seconds)", min_value=3, max_value=30, value=5)
if st.sidebar.button("Refresh now"):
    st.rerun()
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ---------------- Main ----------------
st.title("📊 Real-Time Retail Analytics Dashboard")
st.caption("Live simulated order feed — Kaggle retail dataset replayed through AWS (S3 + DynamoDB + EC2)")

df = fetch_all_orders()

if df.empty:
    st.warning(
        "No orders found yet in DynamoDB. Make sure `simulate_orders.py` is running "
        "and writing to the same table/region as this dashboard."
    )
else:
    # ---- KPI row ----
    total_revenue = df["total_revenue"].sum()
    total_profit = df["total_profit"].sum()
    total_orders = len(df)
    avg_order_value = total_revenue / total_orders if total_orders else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders (simulated)", f"{total_orders:,}")
    col2.metric("Total Revenue", f"${total_revenue:,.0f}")
    col3.metric("Total Profit", f"${total_profit:,.0f}")
    col4.metric("Avg Order Value", f"${avg_order_value:,.2f}")

    st.divider()

    left, right = st.columns([2, 1])

    # ---- Revenue trend over order date ----
    with left:
        st.subheader("Revenue Trend")
        if "order_date_parsed" in df.columns:
            trend = (
                df.dropna(subset=["order_date_parsed"])
                .groupby(df["order_date_parsed"].dt.date)["total_revenue"]
                .sum()
                .reset_index()
                .sort_values("order_date_parsed")
            )
            fig = px.line(trend, x="order_date_parsed", y="total_revenue",
                           labels={"order_date_parsed": "Order Date", "total_revenue": "Revenue ($)"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No order date data available yet.")

    # ---- Region-wise sales ----
    with right:
        st.subheader("Sales by Region")
        if "region" in df.columns:
            region_sales = df.groupby("region")["total_revenue"].sum().sort_values(ascending=False).reset_index()
            fig = px.bar(region_sales, x="total_revenue", y="region", orientation="h",
                          labels={"total_revenue": "Revenue ($)", "region": ""})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No region data available yet.")

    st.divider()

    bottom_left, bottom_right = st.columns(2)

    # ---- Top products (Item Type) ----
    with bottom_left:
        st.subheader("Top Products by Revenue")
        if "item_type" in df.columns:
            top_products = (
                df.groupby("item_type")["total_revenue"].sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            fig = px.bar(top_products, x="item_type", y="total_revenue",
                          labels={"item_type": "Item Type", "total_revenue": "Revenue ($)"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No product data available yet.")

    # ---- Recent orders table ----
    with bottom_right:
        st.subheader("Most Recent Simulated Orders")
        display_cols = [c for c in ["ingested_at_parsed", "region", "country", "item_type", "units_sold", "total_revenue"] if c in df.columns]
        if "ingested_at_parsed" in df.columns and display_cols:
            recent = df.sort_values("ingested_at_parsed", ascending=False).head(15)[display_cols]
            st.dataframe(recent, use_container_width=True, hide_index=True)
        else:
            st.info("No recent order data available yet.")

# ---------------- Auto-refresh ----------------
if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()
