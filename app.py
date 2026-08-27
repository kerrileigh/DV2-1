import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="E-Commerce Management Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("Ecommerce_Dataset.csv")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Return_Reason"] = df["Return_Reason"].fillna("No Return")
    df["Return_Flag"] = np.where(df["Returned"] == "Yes", 1, 0)
    df["On_Time_Flag"] = np.where(df["Shipping_Status"] == "On-Time", 1, 0)
    df["Order_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    return df

df = load_data()

st.title("📊 E-Commerce Management Dashboard")

# Sidebar filters
st.sidebar.header("Dashboard Filters")

categories = st.sidebar.multiselect(
    "Product Category",
    options=df["Product_Category"].unique(),
    default=df["Product_Category"].unique()
)

segments = st.sidebar.multiselect(
    "Customer Segment",
    options=df["Customer_Segment"].unique(),
    default=df["Customer_Segment"].unique()
)

shipping = st.sidebar.multiselect(
    "Shipping Status",
    options=df["Shipping_Status"].unique(),
    default=df["Shipping_Status"].unique()
)

# Apply filters
filtered_df = df[
    (df["Product_Category"].isin(categories)) &
    (df["Customer_Segment"].isin(segments)) &
    (df["Shipping_Status"].isin(shipping))
]

# KPIs based on filtered data
total_sales = filtered_df["Total_Sales_GBP"].sum()
average_order = filtered_df["Total_Sales_GBP"].mean()
average_rating = filtered_df["Customer_Rating"].mean()
average_delivery = filtered_df["Delivery_Time_Days"].mean()
return_rate = filtered_df["Return_Flag"].mean() * 100
on_time_rate = filtered_df["On_Time_Flag"].mean() * 100

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total Sales", f"£{total_sales:,.0f}")
col2.metric("Average Order", f"£{average_order:,.0f}")
col3.metric("Customer Rating", f"{average_rating:.2f}/5")
col4.metric("Avg Delivery", f"{average_delivery:.1f} days")
col5.metric("Return Rate", f"{return_rate:.1f}%")
col6.metric("On-Time Delivery", f"{on_time_rate:.1f}%")

# Sales by category chart
category_sales = (
    filtered_df.groupby("Product_Category")["Total_Sales_GBP"]
    .sum()
    .reset_index()
    .sort_values("Total_Sales_GBP", ascending=False)
)

fig = px.bar(
    category_sales,
    x="Product_Category",
    y="Total_Sales_GBP",
    title="Sales by Product Category",
)

fig.update_layout(xaxis_title="Product Category", yaxis_title="Sales (£)")

st.plotly_chart(fig, use_container_width=True)

# Tabs with simple content
tab1, tab2, tab3 = st.tabs(["Executive Dashboard", "Marketing", "Detailed Analysis"])

with tab1:
    st.header("Executive Dashboard")
    st.write("Summary of key metrics and charts.")
    st.dataframe(filtered_df.head(10))

with tab2:
    st.header("Marketing Analysis")
    st.write("Customer segments and preferences.")
    segments_count = filtered_df["Customer_Segment"].value_counts().reset_index()
    segments_count.columns = ["Customer Segment", "Count"]
    st.bar_chart(segments_count.set_index("Customer Segment"))

with tab3:
    st.header("Detailed Analysis")
    st.subheader("Product Performance")
    product_strategy = (
        filtered_df.groupby(["Product_Category", "Product_Name"])
        .agg(
            Sales=("Total_Sales_GBP", "sum"),
            Units=("Quantity_Purchased", "sum"),
            Average_Rating=("Customer_Rating", "mean"),
            Return_Rate=("Return_Flag", "mean")
        )
        .reset_index()
    )
    product_strategy["Return_Rate"] *= 100
    st.dataframe(product_strategy)
    csv = product_strategy.to_csv(index=False)
    st.download_button(
        label="Download Product Analysis",
        data=csv,
        file_name="product_analysis.csv",
        mime="text/csv"
    )