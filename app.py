import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Transactions Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }

    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
    }

    h1 {
        font-weight: 700;
    }

    h2 {
        margin-top: 25px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# TITLE
# ============================================================

st.title("Financial Transactions Data Analysis")
st.markdown(
    "Interactive analysis, cleaning, filtering, statistics and visualization "
    "of the transaction dataset."
)

# ============================================================
# LOAD DATA
# ============================================================

FILE_NAME = "transactions.csv"

try:
    df_raw = pd.read_csv(FILE_NAME)
except FileNotFoundError:
    st.error(
        f"Could not find `{FILE_NAME}`. "
        "Place the CSV file in the same folder as app.py."
    )
    st.stop()

# Keep original data
df = df_raw.copy()

# ============================================================
# DATA CLEANING
# ============================================================

# Standardize column names
df.columns = (
    df.columns
    .str.strip()
    .str.replace(" ", "_")
    .str.lower()
)

# Replace problematic values with NaN
invalid_values = [
    "ERROR",
    "UNKNOWN",
    "error",
    "unknown",
    "",
    " "
]

df = df.replace(invalid_values, np.nan)

# Convert numerical columns
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

# Convert transaction date
if "transaction_date" in df.columns:
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

# ============================================================
# REPAIR / CALCULATE TOTAL SPENT
# ============================================================

if (
    "quantity" in df.columns
    and "price_per_unit" in df.columns
):
    calculated_total = (
        df["quantity"] * df["price_per_unit"]
    )

    # Fill missing total spent values
    if "total_spent" in df.columns:
        df["total_spent"] = df["total_spent"].fillna(
            calculated_total
        )
    else:
        df["total_spent"] = calculated_total

# ============================================================
# ADD DERIVED COLUMNS
# ============================================================

if "transaction_date" in df.columns:
    df["year"] = df["transaction_date"].dt.year
    df["month"] = df["transaction_date"].dt.month
    df["month_name"] = df["transaction_date"].dt.month_name()
    df["day"] = df["transaction_date"].dt.day
    df["day_name"] = df["transaction_date"].dt.day_name()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Dashboard Filters")

# ------------------------------------------------------------
# ITEM FILTER
# ------------------------------------------------------------

if "item" in df.columns:
    item_values = sorted(
        df["item"].dropna().unique().tolist()
    )

    selected_items = st.sidebar.multiselect(
        "Select Item",
        options=item_values,
        default=item_values
    )
else:
    selected_items = []

# ------------------------------------------------------------
# PAYMENT METHOD FILTER
# ------------------------------------------------------------

if "payment_method" in df.columns:
    payment_values = sorted(
        df["payment_method"].dropna().unique().tolist()
    )

    selected_payment = st.sidebar.multiselect(
        "Payment Method",
        options=payment_values,
        default=payment_values
    )
else:
    selected_payment = []

# ------------------------------------------------------------
# LOCATION FILTER
# ------------------------------------------------------------

if "location" in df.columns:
    location_values = sorted(
        df["location"].dropna().unique().tolist()
    )

    selected_location = st.sidebar.multiselect(
        "Location",
        options=location_values,
        default=location_values
    )
else:
    selected_location = []

# ------------------------------------------------------------
# DATE FILTER
# ------------------------------------------------------------

if "transaction_date" in df.columns:

    valid_dates = df["transaction_date"].dropna()

    if len(valid_dates) > 0:

        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        selected_dates = st.sidebar.date_input(
            "Transaction Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_date = pd.to_datetime(selected_dates[0])
            end_date = pd.to_datetime(selected_dates[1])

            df_filtered = df[
                (df["transaction_date"] >= start_date)
                &
                (df["transaction_date"] <= end_date)
            ].copy()
        else:
            df_filtered = df.copy()

    else:
        df_filtered = df.copy()

else:
    df_filtered = df.copy()

# Apply categorical filters

if "item" in df_filtered.columns and selected_items:
    df_filtered = df_filtered[
        df_filtered["item"].isin(selected_items)
    ]

if "payment_method" in df_filtered.columns and selected_payment:
    df_filtered = df_filtered[
        df_filtered["payment_method"].isin(selected_payment)
    ]

if "location" in df_filtered.columns and selected_location:
    df_filtered = df_filtered[
        df_filtered["location"].isin(selected_location)
    ]

# ============================================================
# DASHBOARD OVERVIEW
# ============================================================

st.header("Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

total_transactions = len(df_filtered)

total_revenue = (
    df_filtered["total_spent"].sum()
    if "total_spent" in df_filtered.columns
    else 0
)

average_transaction = (
    df_filtered["total_spent"].mean()
    if "total_spent" in df_filtered.columns
    else 0
)

total_quantity = (
    df_filtered["quantity"].sum()
    if "quantity" in df_filtered.columns
    else 0
)

col1.metric(
    "Total Transactions",
    f"{total_transactions:,}"
)

col2.metric(
    "Total Revenue",
    f"${total_revenue:,.2f}"
)

col3.metric(
    "Average Transaction",
    f"${average_transaction:,.2f}"
)

col4.metric(
    "Total Quantity",
    f"{total_quantity:,.0f}"
)

# ============================================================
# DATA INSPECTION
# ============================================================

st.header("1. Data Inspection")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Dataset",
        "First Rows",
        "Last Rows",
        "Data Information"
    ]
)

with tab1:
    st.subheader("Filtered Dataset")
    st.dataframe(
        df_filtered,
        use_container_width=True,
        height=400
    )

with tab2:
    st.subheader("First 10 Rows")
    st.dataframe(
        df_filtered.head(10),
        use_container_width=True
    )

with tab3:
    st.subheader("Last 10 Rows")
    st.dataframe(
        df_filtered.tail(10),
        use_container_width=True
    )

with tab4:
    st.write("Number of Rows:", df_filtered.shape[0])
    st.write("Number of Columns:", df_filtered.shape[1])

    st.subheader("Column Names")

    st.write(
        list(df_filtered.columns)
    )

# ============================================================
# MISSING VALUE ANALYSIS
# ============================================================

st.header("2. Missing Value Analysis")

missing_data = pd.DataFrame({
    "Column": df.columns,
    "Missing Values": df.isnull().sum().values
})

missing_data["Missing Percentage"] = (
    missing_data["Missing Values"]
    / len(df)
    * 100
)

missing_data = missing_data.sort_values(
    "Missing Values",
    ascending=False
)

st.dataframe(
    missing_data,
    use_container_width=True
)

fig_missing = px.bar(
    missing_data,
    x="Column",
    y="Missing Values",
    title="Missing Values by Column"
)

fig_missing.update_layout(
    template="plotly_white",
    xaxis_tickangle=-45
)

st.plotly_chart(
    fig_missing,
    use_container_width=True
)

# ============================================================
# DATA CLEANING SUMMARY
# ============================================================

st.header("3. Data Cleaning Summary")

cleaning_col1, cleaning_col2, cleaning_col3 = st.columns(3)

original_rows = len(df_raw)
cleaned_rows = len(df)

missing_before = df_raw.isnull().sum().sum()
missing_after = df.isnull().sum().sum()

cleaning_col1.metric(
    "Original Rows",
    f"{original_rows:,}"
)

cleaning_col2.metric(
    "Missing Values Before Cleaning",
    f"{missing_before:,}"
)

cleaning_col3.metric(
    "Missing Values After Cleaning",
    f"{missing_after:,}"
)

st.write(
    "The cleaning process converts invalid entries such as "
    "`ERROR` and `UNKNOWN` into missing values and converts "
    "numeric and date columns into appropriate data types."
)

# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================

st.header("4. Descriptive Statistics")

numeric_df = df_filtered.select_dtypes(
    include=np.number
)

if not numeric_df.empty:
    st.dataframe(
        numeric_df.describe().T,
        use_container_width=True
    )
else:
    st.info("No numeric columns available.")

# ============================================================
# SORTING
# ============================================================

st.header("5. Sort Transactions")

if "total_spent" in df_filtered.columns:

    sort_option = st.selectbox(
        "Sort by",
        options=[
            "total_spent",
            "quantity",
            "price_per_unit"
        ]
    )

    sort_order = st.radio(
        "Sort Order",
        ["Descending", "Ascending"],
        horizontal=True
    )

    ascending = sort_order == "Ascending"

    sorted_df = df_filtered.sort_values(
        by=sort_option,
        ascending=ascending
    )

    st.dataframe(
        sorted_df.head(100),
        use_container_width=True
    )

# ============================================================
# TOP PRODUCTS
# ============================================================

st.header("6. Product Analysis")

if "item" in df_filtered.columns:

    product_summary = (
        df_filtered
        .groupby("item", dropna=True)
        .agg(
            Transactions=("item", "count"),
            Quantity=("quantity", "sum"),
            Revenue=("total_spent", "sum"),
            Average_Spending=("total_spent", "mean")
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    st.dataframe(
        product_summary,
        use_container_width=True
    )

    fig_product = px.bar(
        product_summary,
        x="item",
        y="Revenue",
        title="Revenue by Product",
        text_auto=".2s"
    )

    fig_product.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_product,
        use_container_width=True
    )

# ============================================================
# QUANTITY BY PRODUCT
# ============================================================

if "item" in df_filtered.columns:

    quantity_summary = (
        df_filtered
        .groupby("item")["quantity"]
        .sum()
        .reset_index()
        .sort_values(
            "quantity",
            ascending=False
        )
    )

    fig_quantity = px.bar(
        quantity_summary,
        x="item",
        y="quantity",
        title="Quantity Sold by Product",
        text_auto=True
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

st.header("7. Payment Method Analysis")

if "payment_method" in df_filtered.columns:

    payment_summary = (
        df_filtered
        .groupby("payment_method")
        .agg(
            Transactions=("payment_method", "count"),
            Revenue=("total_spent", "sum")
        )
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_payment = px.bar(
            payment_summary,
            x="payment_method",
            y="Transactions",
            title="Transactions by Payment Method",
            text_auto=True
        )

        fig_payment.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig_payment,
            use_container_width=True
        )

    with col2:

        fig_payment_pie = px.pie(
            payment_summary,
            names="payment_method",
            values="Revenue",
            title="Revenue Distribution by Payment Method"
        )

        fig_payment_pie.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig_payment_pie,
            use_container_width=True
        )

# ============================================================
# LOCATION ANALYSIS
# ============================================================

st.header("8. Location Analysis")

if "location" in df_filtered.columns:

    location_summary = (
        df_filtered
        .groupby("location")
        .agg(
            Transactions=("location", "count"),
            Revenue=("total_spent", "sum"),
            Quantity=("quantity", "sum")
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    st.dataframe(
        location_summary,
        use_container_width=True
    )

    fig_location = px.bar(
        location_summary,
        x="location",
        y="Revenue",
        title="Revenue by Location",
        text_auto=".2s"
    )

    fig_location.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_location,
        use_container_width=True
    )

# ============================================================
# TIME ANALYSIS
# ============================================================

st.header("9. Time Series Analysis")

if "transaction_date" in df_filtered.columns:

    monthly_data = (
        df_filtered
        .dropna(subset=["transaction_date"])
        .set_index("transaction_date")
        .resample("ME")
        .agg(
            Transactions=("total_spent", "count"),
            Revenue=("total_spent", "sum")
        )
        .reset_index()
    )

    fig_monthly = px.line(
        monthly_data,
        x="transaction_date",
        y="Revenue",
        markers=True,
        title="Monthly Revenue Trend"
    )

    fig_monthly.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )

    fig_transactions = px.line(
        monthly_data,
        x="transaction_date",
        y="Transactions",
        markers=True,
        title="Monthly Transaction Trend"
    )

    fig_transactions.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_transactions,
        use_container_width=True
    )

# ============================================================
# DAILY ANALYSIS
# ============================================================

if "transaction_date" in df_filtered.columns:

    daily_data = (
        df_filtered
        .dropna(subset=["transaction_date"])
        .groupby("transaction_date")
        .agg(
            Revenue=("total_spent", "sum"),
            Transactions=("total_spent", "count")
        )
        .reset_index()
    )

    fig_daily = px.line(
        daily_data,
        x="transaction_date",
        y="Revenue",
        title="Daily Revenue Trend"
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

st.header("10. Transaction Amount Analysis")

if "total_spent" in df_filtered.columns:

    col1, col2 = st.columns(2)

    with col1:

        fig_hist = px.histogram(
            df_filtered,
            x="total_spent",
            nbins=30,
            title="Distribution of Transaction Amounts"
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
            df_filtered,
            y="total_spent",
            title="Transaction Amount Box Plot"
        )

        fig_box.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig_box,
            use_container_width=True
        )

# ============================================================
# QUANTITY VS TOTAL SPENT
# ============================================================

st.header("11. Quantity vs Total Spending")

if (
    "quantity" in df_filtered.columns
    and "total_spent" in df_filtered.columns
):

    scatter_df = df_filtered.dropna(
        subset=[
            "quantity",
            "total_spent"
        ]
    )

    fig_scatter = px.scatter(
        scatter_df,
        x="quantity",
        y="total_spent",
        color="item" if "item" in scatter_df.columns else None,
        hover_data=[
            column
            for column in [
                "transaction_id",
                "item",
                "payment_method",
                "location"
            ]
            if column in scatter_df.columns
        ],
        title="Quantity vs Total Spending"
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
    "price_per_unit" in df_filtered.columns
    and "quantity" in df_filtered.columns
):

    price_quantity_df = df_filtered.dropna(
        subset=[
            "price_per_unit",
            "quantity"
        ]
    )

    fig_price_quantity = px.scatter(
        price_quantity_df,
        x="price_per_unit",
        y="quantity",
        color="item" if "item" in price_quantity_df.columns else None,
        title="Price Per Unit vs Quantity"
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

st.header("12. Correlation Analysis")

correlation_columns = [
    column
    for column in [
        "quantity",
        "price_per_unit",
        "total_spent"
    ]
    if column in df_filtered.columns
]

if len(correlation_columns) >= 2:

    correlation_matrix = (
        df_filtered[correlation_columns]
        .corr()
    )

    fig_corr = px.imshow(
        correlation_matrix,
        text_auto=".2f",
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

    st.dataframe(
        correlation_matrix,
        use_container_width=True
    )

# ============================================================
# OUTLIER ANALYSIS
# ============================================================

st.header("13. Outlier Analysis")

if "total_spent" in df_filtered.columns:

    outlier_data = df_filtered.dropna(
        subset=["total_spent"]
    ).copy()

    Q1 = outlier_data["total_spent"].quantile(0.25)
    Q3 = outlier_data["total_spent"].quantile(0.75)

    IQR = Q3 - Q1

    lower_limit = Q1 - 1.5 * IQR
    upper_limit = Q3 + 1.5 * IQR

    outliers = outlier_data[
        (outlier_data["total_spent"] < lower_limit)
        |
        (outlier_data["total_spent"] > upper_limit)
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Q1",
        f"${Q1:,.2f}"
    )

    col2.metric(
        "Q3",
        f"${Q3:,.2f}"
    )

    col3.metric(
        "Number of Outliers",
        f"{len(outliers):,}"
    )

    st.write(
        f"Lower Bound: ${lower_limit:,.2f}"
    )

    st.write(
        f"Upper Bound: ${upper_limit:,.2f}"
    )

    st.subheader("Detected Outliers")

    st.dataframe(
        outliers,
        use_container_width=True
    )

# ============================================================
# TOP TRANSACTIONS
# ============================================================

st.header("14. Top Transactions")

if "total_spent" in df_filtered.columns:

    top_transactions = (
        df_filtered
        .sort_values(
            "total_spent",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        top_transactions,
        use_container_width=True
    )

# ============================================================
# SUMMARY BY ITEM
# ============================================================

st.header("15. Summary by Item")

if "item" in df_filtered.columns:

    item_analysis = (
        df_filtered
        .groupby("item")
        .agg(
            Total_Transactions=("item", "count"),
            Total_Quantity=("quantity", "sum"),
            Total_Revenue=("total_spent", "sum"),
            Average_Revenue=("total_spent", "mean"),
            Maximum_Transaction=("total_spent", "max"),
            Minimum_Transaction=("total_spent", "min")
        )
        .reset_index()
    )

    st.dataframe(
        item_analysis,
        use_container_width=True
    )

# ============================================================
# DATA DOWNLOAD
# ============================================================

st.header("16. Download Data")

csv_data = df_filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_transactions.csv",
    mime="text/csv"
)

# ============================================================
# ORIGINAL DATA DOWNLOAD
# ============================================================

original_csv = df_raw.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Original Dataset",
    data=original_csv,
    file_name="original_transactions.csv",
    mime="text/csv"
)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    "Financial Transactions Data Analysis Dashboard"
)