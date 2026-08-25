import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="E-Commerce Management Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():

    df = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/Ecommerce/Ecommerce_Dataset.csv")

    df["Order_Date"] = pd.to_datetime(df["Order_Date"])

    df["Return_Reason"] = df["Return_Reason"].fillna("No Return")

    df["Return_Flag"] = np.where(
        df["Returned"] == "Yes", 1, 0
    )

    df["On_Time_Flag"] = np.where(
        df["Shipping_Status"] == "On-Time", 1, 0
    )

    df["Order_Month"] = (
        df["Order_Date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df


df = load_data()

st.title("📊 E-Commerce Management Dashboard")

st.markdown("""
### Business Performance Overview

Monitor sales performance, customer satisfaction,
delivery efficiency and product strategy.
""")

total_sales = df["Total_Sales_GBP"].sum()

average_order = df["Total_Sales_GBP"].mean()

average_rating = df["Customer_Rating"].mean()

average_delivery = df["Delivery_Time_Days"].mean()

return_rate = df["Return_Flag"].mean() * 100

on_time_rate = df["On_Time_Flag"].mean() * 100

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Total Sales",
    f"£{total_sales:,.0f}"
)

col2.metric(
    "Average Order",
    f"£{average_order:,.0f}"
)

col3.metric(
    "Customer Rating",
    f"{average_rating:.2f}/5"
)

col4.metric(
    "Avg Delivery",
    f"{average_delivery:.1f} days"
)

col5.metric(
    "Return Rate",
    f"{return_rate:.1f}%"
)

col6.metric(
    "On-Time Delivery",
    f"{on_time_rate:.1f}%"
)

category_sales = (
    df.groupby("Product_Category")["Total_Sales_GBP"]
    .sum()
    .reset_index()
    .sort_values("Total_Sales_GBP", ascending=False)
)

fig = px.bar(
    category_sales,
    x="Product_Category",
    y="Total_Sales_GBP",
    title="Sales by Product Category",
    text_auto=".2s"
)

fig.update_layout(
    xaxis_title="Product Category",
    yaxis_title="Sales (£)"
)

st.plotly_chart(
    fig,
    width=True
)

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        category_sales,
        x="Product_Category",
        y="Total_Sales_GBP",
        title="Sales by Category"
    )

    st.plotly_chart(
        fig,
        width=True
    )


with col2:

    monthly_sales = (
        df.groupby("Order_Month")["Total_Sales_GBP"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly_sales,
        x="Order_Month",
        y="Total_Sales_GBP",
        markers=True,
        title="Monthly Sales Trend"
    )

    st.plotly_chart(
        fig,
        width=True
    )

rating_by_shipping = (
    df.groupby("Shipping_Status")
    .agg(
        Average_Rating=("Customer_Rating", "mean"),
        Average_Delivery=("Delivery_Time_Days", "mean")
    )
    .reset_index()
)

fig = px.bar(
    rating_by_shipping,
    x="Shipping_Status",
    y="Average_Rating",
    title="Customer Satisfaction by Delivery Status",
    text_auto=".2f"
)

fig.update_yaxes(range=[0, 5])

st.plotly_chart(
    fig,
    width=True
)

fig = px.scatter(
    df,
    x="Delivery_Time_Days",
    y="Customer_Rating",
    color="Shipping_Status",
    hover_data=[
        "Product_Name",
        "Product_Category",
        "Location",
        "Customer_Segment"
    ],
    title="Delivery Time vs Customer Rating"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

returns = (
    df[df["Returned"] == "Yes"]
    .groupby("Return_Reason")
    .size()
    .reset_index(name="Returns")
    .sort_values("Returns", ascending=False)
)

fig = px.bar(
    returns,
    x="Returns",
    y="Return_Reason",
    orientation="h",
    title="Returns by Reason"
)

st.plotly_chart(
    fig,
    width=True
)

product_strategy = (
    df.groupby(["Product_Category", "Product_Name"])
    .agg(
        Sales=("Total_Sales_GBP", "sum"),
        Units=("Quantity_Purchased", "sum"),
        Average_Rating=("Customer_Rating", "mean"),
        Return_Rate=("Return_Flag", "mean")
    )
    .reset_index()
)

product_strategy["Return_Rate"] *= 100

fig = px.scatter(
    product_strategy,
    x="Average_Rating",
    y="Sales",
    size="Units",
    color="Product_Category",
    hover_name="Product_Name",
    hover_data=["Return_Rate"],
    title="Product Strategy: Sales vs Customer Rating"
)

st.plotly_chart(
    fig,
    width=True
)

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

filtered_df = df[
    (df["Product_Category"].isin(categories)) &
    (df["Customer_Segment"].isin(segments)) &
    (df["Shipping_Status"].isin(shipping))
]

tab1, tab2, tab3 = st.tabs([
    "Executive Dashboard",
    "Marketing",
    "Detailed Analysis"
])

with tab1:

    st.header("Executive Dashboard")

    # KPIs
    # Sales charts
    # Delivery charts
    # Customer satisfaction


with tab2:

    st.header("Marketing Analysis")

    # Customer segments
    # Age groups
    # Locations
    # Product preferences


with tab3:

    st.header("Detailed Analysis")

    st.subheader("Product Performance")

    st.dataframe(
        product_strategy,
        width=True
    )

    csv = product_strategy.to_csv(index=False)

    st.download_button(
        label="Download Product Analysis",
        data=csv,
        file_name="product_analysis.csv",
        mime="text/csv"
    )
