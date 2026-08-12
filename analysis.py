"""
Core data-analysis logic. Loads an e-commerce orders CSV with pandas,
computes summary KPIs, and renders a set of seaborn charts as base64
PNG strings so they can be dropped straight into an HTML <img> tag.
"""
import base64
import io

import matplotlib
matplotlib.use("Agg")  # no GUI backend needed on a server
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="deep")

REQUIRED_COLUMNS = {"order_date", "category", "revenue"}


def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV is missing required column(s): {', '.join(sorted(missing))}. "
            f"Required columns: {', '.join(sorted(REQUIRED_COLUMNS))}"
        )

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"])
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df = df.dropna(subset=["revenue"])
    return df


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def compute_kpis(df: pd.DataFrame) -> dict:
    kpis = {
        "total_revenue": round(df["revenue"].sum(), 2),
        "total_orders": int(len(df)),
        "avg_order_value": round(df["revenue"].mean(), 2),
        "date_range": f"{df['order_date'].min().date()} to {df['order_date'].max().date()}",
    }
    if "customer_id" in df.columns:
        kpis["unique_customers"] = int(df["customer_id"].nunique())
    if "rating" in df.columns:
        kpis["avg_rating"] = round(df["rating"].mean(), 2)
    return kpis


def chart_revenue_trend(df: pd.DataFrame) -> str:
    monthly = df.set_index("order_date").resample("ME")["revenue"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.lineplot(data=monthly, x="order_date", y="revenue", marker="o", ax=ax, color="#4C72B0")
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    fig.autofmt_xdate()
    return _fig_to_base64(fig)


def chart_revenue_by_category(df: pd.DataFrame) -> str:
    cat_rev = (
        df.groupby("category")["revenue"].sum().sort_values(ascending=False).reset_index()
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=cat_rev, x="revenue", y="category", hue="category", legend=False, ax=ax, palette="viridis")
    ax.set_title("Revenue by Category")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("")
    return _fig_to_base64(fig)


def chart_order_status(df: pd.DataFrame) -> str | None:
    if "order_status" not in df.columns:
        return None
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    status_counts = df["order_status"].value_counts()
    ax.pie(
        status_counts.values,
        labels=status_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("Set2", len(status_counts)),
    )
    ax.set_title("Order Status Breakdown")
    return _fig_to_base64(fig)


def chart_top_regions(df: pd.DataFrame) -> str | None:
    if "region" not in df.columns:
        return None
    region_rev = df.groupby("region")["revenue"].sum().sort_values(ascending=False).reset_index()
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=region_rev, x="region", y="revenue", hue="region", legend=False, ax=ax, palette="mako")
    ax.set_title("Revenue by Region")
    ax.set_xlabel("")
    ax.set_ylabel("Revenue")
    return _fig_to_base64(fig)


def chart_age_distribution(df: pd.DataFrame) -> str | None:
    if "customer_age" not in df.columns:
        return None
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(df["customer_age"], bins=20, kde=True, ax=ax, color="#DD8452")
    ax.set_title("Customer Age Distribution")
    ax.set_xlabel("Age")
    return _fig_to_base64(fig)


def chart_correlation_heatmap(df: pd.DataFrame) -> str | None:
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        return None
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax, center=0)
    ax.set_title("Correlation Heatmap (Numeric Fields)")
    return _fig_to_base64(fig)


def chart_price_vs_quantity(df: pd.DataFrame) -> str | None:
    if not {"product_price", "quantity"}.issubset(df.columns):
        return None
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.scatterplot(
        data=df.sample(min(len(df), 800), random_state=1),
        x="product_price", y="quantity", hue="category" if "category" in df.columns else None,
        alpha=0.6, ax=ax,
    )
    ax.set_title("Product Price vs Quantity Ordered")
    ax.set_xlabel("Product Price")
    ax.set_ylabel("Quantity")
    if "category" in df.columns:
        ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    return _fig_to_base64(fig)


def build_dashboard(filepath: str) -> dict:
    """Loads the CSV and returns KPIs + all chart images (base64) in one dict."""
    df = load_data(filepath)

    charts = {
        "revenue_trend": chart_revenue_trend(df),
        "revenue_by_category": chart_revenue_by_category(df),
        "order_status": chart_order_status(df),
        "revenue_by_region": chart_top_regions(df),
        "age_distribution": chart_age_distribution(df),
        "correlation_heatmap": chart_correlation_heatmap(df),
        "price_vs_quantity": chart_price_vs_quantity(df),
    }
    # drop charts that returned None (column not present in this dataset)
    charts = {k: v for k, v in charts.items() if v is not None}

    return {
        "kpis": compute_kpis(df),
        "charts": charts,
        "columns": list(df.columns),
        "row_count": len(df),
    }
