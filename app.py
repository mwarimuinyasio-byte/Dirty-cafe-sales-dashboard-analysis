import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Dirty Cafe Sales Dashboard",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("Dirty Cafe Sales Dashboard")
st.write("Interactive sales data analysis and visualization dashboard.")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("dirty_cafe_sales.csv")
    except FileNotFoundError:
        try:
            df = pd.read_csv("dirty_cafe_sales.csv")
        except FileNotFoundError:
            st.error(
                "The CSV file was not found. Make sure "
                "'dirty_cafe_sales.csv' is in the same folder as app.py."
            )
            st.stop()

    return df


df = load_data()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)


# ============================================================
# REPLACE INVALID VALUES
# ============================================================

invalid_values = [
    "ERROR",
    "Error",
    "error",
    "UNKNOWN",
    "Unknown",
    "unknown",
    "",
    " "
]

df = df.replace(invalid_values, np.nan)


# ============================================================
# DATA CLEANING
# ============================================================

numeric_columns = [
    "quantity",
    "price_per_unit",
    "total_spent"
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


if "transaction_date" in df.columns:
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )


# ============================================================
# CALCULATE TOTAL SPENT
# ============================================================

if (
    "quantity" in df.columns
    and "price_per_unit" in df.columns
):
    calculated_total = (
        df["quantity"] * df["price_per_unit"]
    )

    if "total_spent" not in df.columns:
        df["total_spent"] = calculated_total

    else:
        df["total_spent"] = df["total_spent"].fillna(
            calculated_total
        )


# ============================================================
# DATE FEATURES
# ============================================================

if "transaction_date" in df.columns:

    df["year"] = df["transaction_date"].dt.year

    df["month"] = df["transaction_date"].dt.month

    df["month_name"] = (
        df["transaction_date"]
        .dt.month_name()
    )

    df["day"] = df["transaction_date"].dt.day

    df["day_name"] = (
        df["transaction_date"]
        .dt.day_name()
    )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")


filtered_df = df.copy()


# Item filter
if "item" in df.columns:

    items = sorted(
        df["item"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_items = st.sidebar.multiselect(
        "Select Item",
        items,
        default=items
    )

    if selected_items:
        filtered_df = filtered_df[
            filtered_df["item"]
            .astype(str)
            .isin(selected_items)
        ]


# Payment method filter
if "payment_method" in df.columns:

    payment_methods = sorted(
        df["payment_method"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_payment = st.sidebar.multiselect(
        "Payment Method",
        payment_methods,
        default=payment_methods
    )

    if selected_payment:
        filtered_df = filtered_df[
            filtered_df["payment_method"]
            .astype(str)
            .isin(selected_payment)
        ]


# Location filter
if "location" in df.columns:

    locations = sorted(
        df["location"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_locations = st.sidebar.multiselect(
        "Location",
        locations,
        default=locations
    )

    if selected_locations:
        filtered_df = filtered_df[
            filtered_df["location"]
            .astype(str)
            .isin(selected_locations)
        ]


# Date filter
if (
    "transaction_date" in df.columns
    and df["transaction_date"].notna().any()
):

    min_date = df["transaction_date"].min().date()
    max_date = df["transaction_date"].max().date()

    selected_dates = st.sidebar.date_input(
        "Transaction Date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(selected_dates) == 2:

        start_date = pd.Timestamp(
            selected_dates[0]
        )

        end_date = (
            pd.Timestamp(selected_dates[1])
            + pd.Timedelta(days=1)
        )

        filtered_df = filtered_df[
            (
                filtered_df["transaction_date"]
                >= start_date
            )
            &
            (
                filtered_df["transaction_date"]
                < end_date
            )
        ]


# ============================================================
# CHECK FILTERED DATA
# ============================================================

if filtered_df.empty:

    st.warning(
        "No records match the selected filters."
    )

    st.stop()


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)


# Total transactions
with col1:
    st.metric(
        "Total Transactions",
        f"{len(filtered_df):,}"
    )


# Total revenue
with col2:

    if "total_spent" in filtered_df.columns:

        total_revenue = (
            filtered_df["total_spent"]
            .sum()
        )

        st.metric(
            "Total Revenue",
            f"{total_revenue:,.2f}"
        )

    else:
        st.metric(
            "Total Revenue",
            "N/A"
        )


# Average transaction
with col3:

    if "total_spent" in filtered_df.columns:

        average_transaction = (
            filtered_df["total_spent"]
            .mean()
        )

        st.metric(
            "Average Transaction",
            f"{average_transaction:,.2f}"
        )

    else:
        st.metric(
            "Average Transaction",
            "N/A"
        )


# Total quantity
with col4:

    if "quantity" in filtered_df.columns:

        total_quantity = (
            filtered_df["quantity"]
            .sum()
        )

        st.metric(
            "Total Quantity",
            f"{total_quantity:,.0f}"
        )

    else:
        st.metric(
            "Total Quantity",
            "N/A"
        )


# ============================================================
# DATASET INFORMATION
# ============================================================

st.subheader("Dataset Overview")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Full Dataset",
        "First 5 Rows",
        "Last 10 Rows",
        "Data Information"
    ]
)


with tab1:

    st.dataframe(
        filtered_df,
        use_container_width=True
    )


with tab2:

    st.dataframe(
        filtered_df.head(),
        use_container_width=True
    )


with tab3:

    st.dataframe(
        filtered_df.tail(10),
        use_container_width=True
    )


with tab4:

    info_df = pd.DataFrame({
        "Column": filtered_df.columns,
        "Data Type": [
            str(dtype)
            for dtype in filtered_df.dtypes
        ],
        "Missing Values": [
            filtered_df[column].isna().sum()
            for column in filtered_df.columns
        ],
        "Unique Values": [
            filtered_df[column].nunique()
            for column in filtered_df.columns
        ]
    })

    st.dataframe(
        info_df,
        use_container_width=True
    )


# ============================================================
# MISSING VALUES
# ============================================================

st.subheader("Missing Value Analysis")

missing_df = pd.DataFrame({
    "Column": df.columns,
    "Missing Values": [
        df[column].isna().sum()
        for column in df.columns
    ]
})

missing_df["Missing Percentage"] = (
    missing_df["Missing Values"]
    / len(df)
    * 100
)

missing_df = missing_df.sort_values(
    "Missing Values",
    ascending=False
)

st.dataframe(
    missing_df,
    use_container_width=True
)


# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================

st.subheader("Descriptive Statistics")

numeric_df = filtered_df.select_dtypes(
    include=np.number
)

if not numeric_df.empty:

    st.dataframe(
        numeric_df.describe().T,
        use_container_width=True
    )

else:

    st.info(
        "No numeric columns are available."
    )


# ============================================================
# ITEM ANALYSIS
# ============================================================

if "item" in filtered_df.columns:

    st.subheader("Item Analysis")

    item_sales = (
        filtered_df
        .groupby("item", as_index=False)
        ["total_spent"]
        .sum()
        .sort_values(
            "total_spent",
            ascending=False
        )
    )

    fig_item = px.bar(
        item_sales,
        x="item",
        y="total_spent",
        title="Revenue by Item",
        labels={
            "item": "Item",
            "total_spent": "Total Revenue"
        }
    )

    fig_item.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_item,
        use_container_width=True
    )


# ============================================================
# QUANTITY BY ITEM
# ============================================================

if (
    "item" in filtered_df.columns
    and "quantity" in filtered_df.columns
):

    quantity_by_item = (
        filtered_df
        .groupby("item", as_index=False)
        ["quantity"]
        .sum()
        .sort_values(
            "quantity",
            ascending=False
        )
    )

    fig_quantity = px.bar(
        quantity_by_item,
        x="item",
        y="quantity",
        title="Quantity Sold by Item",
        labels={
            "item": "Item",
            "quantity": "Quantity Sold"
        }
    )

    fig_quantity.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_quantity,
        use_container_width=True
    )


# ============================================================
# PAYMENT METHOD ANALYSIS
# ============================================================

if "payment_method" in filtered_df.columns:

    st.subheader("Payment Method Analysis")

    payment_counts = (
        filtered_df["payment_method"]
        .value_counts()
        .reset_index()
    )

    payment_counts.columns = [
        "payment_method",
        "count"
    ]

    fig_payment = px.pie(
        payment_counts,
        names="payment_method",
        values="count",
        title="Transactions by Payment Method",
        hole=0.3
    )

    fig_payment.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_payment,
        use_container_width=True
    )


# ============================================================
# LOCATION ANALYSIS
# ============================================================

if "location" in filtered_df.columns:

    st.subheader("Location Analysis")

    location_sales = (
        filtered_df
        .groupby("location", as_index=False)
        ["total_spent"]
        .sum()
        .sort_values(
            "total_spent",
            ascending=False
        )
    )

    fig_location = px.bar(
        location_sales,
        x="location",
        y="total_spent",
        title="Revenue by Location",
        labels={
            "location": "Location",
            "total_spent": "Revenue"
        }
    )

    fig_location.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_location,
        use_container_width=True
    )


# ============================================================
# MONTHLY SALES TREND
# ============================================================

if (
    "transaction_date" in filtered_df.columns
    and "total_spent" in filtered_df.columns
):

    st.subheader("Monthly Sales Trend")

    monthly_sales = (
        filtered_df
        .dropna(subset=["transaction_date"])
        .set_index("transaction_date")
        ["total_spent"]
        .resample("ME")
        .sum()
        .reset_index()
    )

    fig_monthly = px.line(
        monthly_sales,
        x="transaction_date",
        y="total_spent",
        markers=True,
        title="Monthly Revenue Trend",
        labels={
            "transaction_date": "Month",
            "total_spent": "Revenue"
        }
    )

    fig_monthly.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )


# ============================================================
# DAILY SALES
# ============================================================

if (
    "transaction_date" in filtered_df.columns
    and "total_spent" in filtered_df.columns
):

    daily_sales = (
        filtered_df
        .dropna(subset=["transaction_date"])
        .groupby(
            filtered_df[
                "transaction_date"
            ].dt.date
        )["total_spent"]
        .sum()
        .reset_index()
    )

    daily_sales.columns = [
        "date",
        "total_spent"
    ]

    fig_daily = px.line(
        daily_sales,
        x="date",
        y="total_spent",
        title="Daily Revenue Trend",
        labels={
            "date": "Date",
            "total_spent": "Revenue"
        }
    )

    fig_daily.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_daily,
        use_container_width=True
    )


# ============================================================
# TRANSACTION AMOUNT DISTRIBUTION
# ============================================================

if "total_spent" in filtered_df.columns:

    st.subheader("Transaction Amount Analysis")

    col1, col2 = st.columns(2)

    with col1:

        fig_hist = px.histogram(
            filtered_df,
            x="total_spent",
            nbins=40,
            title="Transaction Amount Distribution",
            labels={
                "total_spent": "Transaction Amount"
            }
        )

        fig_hist.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True
        )

    with col2:

        fig_box = px.box(
            filtered_df,
            y="total_spent",
            title="Transaction Amount Box Plot",
            labels={
                "total_spent": "Transaction Amount"
            }
        )

        fig_box.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig_box,
            use_container_width=True
        )


# ============================================================
# QUANTITY VS SPENDING
# ============================================================

if (
    "quantity" in filtered_df.columns
    and "total_spent" in filtered_df.columns
):

    fig_scatter = px.scatter(
        filtered_df,
        x="quantity",
        y="total_spent",
        title="Quantity vs Total Spending",
        labels={
            "quantity": "Quantity",
            "total_spent": "Total Spending"
        },
        trendline="ols"
    )

    fig_scatter.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )


# ============================================================
# PRICE VS QUANTITY
# ============================================================

if (
    "price_per_unit" in filtered_df.columns
    and "quantity" in filtered_df.columns
):

    fig_price_quantity = px.scatter(
        filtered_df,
        x="price_per_unit",
        y="quantity",
        title="Price per Unit vs Quantity",
        labels={
            "price_per_unit": "Price per Unit",
            "quantity": "Quantity"
        }
    )

    fig_price_quantity.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_price_quantity,
        use_container_width=True
    )


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

st.subheader("Correlation Analysis")

correlation_df = (
    filtered_df
    .select_dtypes(include=np.number)
    .corr()
)

if not correlation_df.empty:

    fig_corr = px.imshow(
        correlation_df,
        text_auto=True,
        aspect="auto",
        title="Correlation Heatmap"
    )

    fig_corr.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_corr,
        use_container_width=True
    )


# ============================================================
# OUTLIER ANALYSIS
# ============================================================

if "total_spent" in filtered_df.columns:

    st.subheader("Outlier Analysis")

    q1 = filtered_df[
        "total_spent"
    ].quantile(0.25)

    q3 = filtered_df[
        "total_spent"
    ].quantile(0.75)

    iqr = q3 - q1

    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    outliers = filtered_df[
        (
            filtered_df["total_spent"]
            < lower_limit
        )
        |
        (
            filtered_df["total_spent"]
            > upper_limit
        )
    ]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Q1",
            f"{q1:,.2f}"
        )

    with col2:
        st.metric(
            "Q3",
            f"{q3:,.2f}"
        )

    with col3:
        st.metric(
            "Number of Outliers",
            f"{len(outliers):,}"
        )

    st.dataframe(
        outliers,
        use_container_width=True
    )


# ============================================================
# TOP 10 TRANSACTIONS
# ============================================================

if "total_spent" in filtered_df.columns:

    st.subheader("Top 10 Highest Transactions")

    top_transactions = (
        filtered_df
        .sort_values(
            "total_spent",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_transactions,
        use_container_width=True
    )


# ============================================================
# SUMMARY BY ITEM
# ============================================================

if (
    "item" in filtered_df.columns
    and "total_spent" in filtered_df.columns
):

    st.subheader("Item Summary")

    item_summary = (
        filtered_df
        .groupby("item")
        .agg(
            Total_Revenue=(
                "total_spent",
                "sum"
            ),
            Average_Revenue=(
                "total_spent",
                "mean"
            ),
            Number_of_Transactions=(
                "total_spent",
                "count"
            )
        )
        .reset_index()
        .sort_values(
            "Total_Revenue",
            ascending=False
        )
    )

    st.dataframe(
        item_summary,
        use_container_width=True
    )


# ============================================================
# DOWNLOAD DATA
# ============================================================

st.subheader("Download Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv_data,
    file_name="dirty_cafe_sales_filtered.csv",
    mime="text/csv"
)


original_csv = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Cleaned Dataset",
    data=original_csv,
    file_name="dirty_cafe_sales_cleaned.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.write(
    "Dirty Cafe Sales Dashboard | "
    "Built with Python, Pandas, NumPy, Streamlit and Plotly"
)