import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="E-Commerce Management Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Ecommerce_Dataset.csv")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Return_Reason"] = df["Return_Reason"].fillna("No Return")
    df["Return_Flag"] = np.where(df["Returned"] == "Yes", 1, 0)
    df["On_Time_Flag"] = np.where(df["Shipping_Status"] == "On-Time", 1, 0)
    df["Order_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    
    # Add Delivery_Band column for delivery time categories
    df["Delivery_Band"] = pd.cut(
        df["Delivery_Time_Days"],
        bins=[0, 3, 5, 7, 10, np.inf],
        labels=["1-3 Days", "4-5 Days", "6-7 Days", "8-10 Days", "10+ Days"],
        right=True,
        include_lowest=True
    )
    
    return df

# Load data
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

# Tabs with content
tab1, tab2, tab3 = st.tabs(["Executive Dashboard", "Marketing", "Detailed Analysis"])

with tab1:
    st.header("Executive Dashboard")
    st.write("Summary of key metrics and charts.")
    st.dataframe(filtered_df.head(10))

    # Two visualisations side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Delivery Time vs Customer Rating")
        plt.figure(figsize=(9, 6))
        sns.scatterplot(
            data=filtered_df,
            x="Delivery_Time_Days",
            y="Customer_Rating",
            alpha=0.6
        )
        sns.regplot(
            data=filtered_df,
            x="Delivery_Time_Days",
            y="Customer_Rating",
            scatter=False,
            color='orange'
        )
        plt.title("Delivery Time vs Customer Rating")
        plt.xlabel("Delivery Time (Days)")
        plt.ylabel("Customer Rating")
        st.pyplot(plt.gcf())
        plt.clf()

    with col2:
        st.subheader("Average Customer Rating by Delivery Performance")
        rating_by_delivery = filtered_df.pivot_table(
            index="Delivery_Band",
            columns="Shipping_Status",
            values="Customer_Rating",
            aggfunc="mean"
        )
        plt.figure(figsize=(8, 5))
        sns.heatmap(
            rating_by_delivery,
            annot=True,
            fmt=".2f",
            cmap="YlGnBu"
        )
        plt.title("Average Customer Rating by Delivery Performance")
        st.pyplot(plt.gcf())
        plt.clf()

    # Additional visualisations under tab1

    # Customer Rating by Delivery Status
    delivery_satisfaction = (
        filtered_df.groupby("Shipping_Status")["Customer_Rating"]
        .mean()
        .reset_index(name="Average_Rating")
    )
    st.subheader("Customer Rating by Delivery Status")
    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=delivery_satisfaction,
        x="Shipping_Status",
        y="Average_Rating"
    )
    plt.title("Customer Rating by Delivery Status")
    plt.xlabel("Shipping Status")
    plt.ylabel("Average Rating")
    st.pyplot(plt.gcf())
    plt.clf()

    # Orders Returned by Reason
    return_reasons = (
        filtered_df[filtered_df["Returned"] == "Yes"]
        .groupby("Return_Reason")
        .size()
        .reset_index(name="Returns")
        .sort_values("Returns", ascending=False)
    )
    st.subheader("Orders Returned by Reason")
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=return_reasons,
        x="Returns",
        y="Return_Reason"
    )
    plt.title("Orders Returned by Reason")
    plt.xlabel("Number of Returns")
    plt.ylabel("Return Reason")
    st.pyplot(plt.gcf())
    plt.clf()

    # Sales by Product
    product_sales = (
        filtered_df.groupby("Product_Name")["Total_Sales_GBP"]
        .sum()
        .reset_index(name="Sales")
        .sort_values("Sales", ascending=False)
        .head(20)  # Limit to top 20 products for readability
    )
    st.subheader("Sales by Product")
    plt.figure(figsize=(10, 7))
    sns.barplot(
        data=product_sales,
        x="Sales",
        y="Product_Name"
    )
    plt.title("Sales by Product")
    plt.xlabel("Sales (£)")
    plt.ylabel("Product")
    st.pyplot(plt.gcf())
    plt.clf()

with tab2:
    st.header("Marketing Analysis")
    st.write("Customer segments and preferences.")

    # Customer segments count
    segments_count = filtered_df["Customer_Segment"].value_counts().reset_index()
    segments_count.columns = ["Customer Segment", "Count"]
    st.bar_chart(segments_count.set_index("Customer Segment"))

    # Sales by Product
    st.subheader("Sales by Product")
    plt.figure(figsize=(10, 7))
    sns.barplot(
        data=product_sales,
        x="Sales",
        y="Product_Name"
    )
    plt.title("Sales by Product")
    plt.xlabel("Sales (£)")
    plt.ylabel("Product")
    st.pyplot(plt.gcf())
    plt.clf()

    # Monthly sales trend
    monthly_sales = (
        filtered_df.groupby("Order_Month")["Total_Sales_GBP"]
        .sum()
        .reset_index()
    )
    st.subheader("Monthly Sales Trend")
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=monthly_sales,
        x="Order_Month",
        y="Total_Sales_GBP",
        marker="o"
    )
    plt.title("Monthly Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Sales (£)")
    plt.xticks(rotation=45)
    st.pyplot(plt.gcf())
    plt.clf()

    # Sales by Location
    location_sales = (
        filtered_df.groupby("Location")["Total_Sales_GBP"]
        .sum()
        .reset_index(name="Sales")
        .sort_values("Sales", ascending=False)
    )
    st.subheader("Sales Performance by Location")
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=location_sales,
        x="Sales",
        y="Location"
    )
    plt.title("Sales Performance by Location")
    plt.xlabel("Sales (£)")
    plt.ylabel("Location")
    st.pyplot(plt.gcf())
    plt.clf()

    # Average Delivery Time by Location
    location_delivery = (
        filtered_df.groupby("Location")["Delivery_Time_Days"]
        .mean()
        .reset_index(name="Average_Delivery")
        .sort_values("Average_Delivery")
    )
    st.subheader("Average Delivery Time by Location")
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=location_delivery,
        x="Average_Delivery",
        y="Location"
    )
    plt.title("Average Delivery Time by Location")
    plt.xlabel("Average Delivery Time (Days)")
    plt.ylabel("Location")
    st.pyplot(plt.gcf())
    plt.clf()

    # Sales by Customer Age Group (if available)
    if "Age_Group" in filtered_df.columns:
        age_analysis = (
            filtered_df.groupby("Age_Group")["Total_Sales_GBP"]
            .sum()
            .reset_index(name="Sales")
            .sort_values("Sales", ascending=False)
        )
        st.subheader("Sales by Customer Age Group")
        plt.figure(figsize=(9, 5))
        sns.barplot(
            data=age_analysis,
            x="Age_Group",
            y="Sales"
        )
        plt.title("Sales by Customer Age Group")
        plt.xlabel("Age Group")
        plt.ylabel("Sales (£)")
        st.pyplot(plt.gcf())
        plt.clf()
    else:
        st.info("No 'Age_Group' column found in data for age analysis.")

with tab3:
    st.header("Detailed Analysis")
    st.subheader("Product Performance")
    product_strategy = (
        filtered_df.groupby(["Product_Name", "Product_Category"])
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