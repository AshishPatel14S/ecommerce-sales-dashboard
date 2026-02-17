"""
E-commerce Sales Dashboard
Interactive dashboard for analyzing online retail performance.

Run: streamlit run demo/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_loader import load_data, check_data_availability
from metrics import (
    calculate_revenue_metrics,
    calculate_customer_metrics,
    calculate_geographic_metrics,
    calculate_time_metrics,
    format_currency,
    format_percentage,
    format_number
)

# Page config
st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    .insight-box {
        background-color: #e8f4ea;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_data():
    """Load and cache data."""
    try:
        df = load_data(use_sample=False)
        return df
    except FileNotFoundError:
        st.error("⚠️ Data not found. Please run preprocessing first.")
        st.code("python src/preprocessing.py", language="bash")
        st.stop()


def render_kpi_cards(metrics: dict):
    """Render the top KPI cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=format_currency(metrics['revenue']['total_revenue']),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Customers",
            value=format_number(metrics['customers']['total_customers']),
            delta=f"{metrics['customers']['repeat_rate']:.1f}% repeat"
        )
    
    with col3:
        st.metric(
            label="Avg Order Value",
            value=format_currency(metrics['customers']['avg_aov']),
            delta=None
        )
    
    with col4:
        st.metric(
            label="Countries",
            value=metrics['geographic']['total_countries'],
            delta=f"UK: {metrics['geographic']['uk_share']:.0f}%"
        )


def render_revenue_trend(df: pd.DataFrame):
    """Render monthly revenue trend chart."""
    st.subheader("📈 Monthly Revenue Trend")
    
    monthly = df.groupby('YearMonth')['Revenue'].sum().reset_index()
    monthly['YearMonth'] = monthly['YearMonth'].astype(str)
    
    fig = px.area(
        monthly,
        x='YearMonth',
        y='Revenue',
        title=None,
        labels={'Revenue': 'Revenue (£)', 'YearMonth': 'Month'}
    )
    
    fig.update_traces(
        fill='tozeroy',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        margin=dict(l=50, r=50, t=30, b=80)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insight box
    peak_month = monthly.loc[monthly['Revenue'].idxmax()]
    st.markdown(f"""
    <div class="insight-box">
        <strong>💡 Insight:</strong> Peak revenue was in <strong>{peak_month['YearMonth']}</strong> 
        with <strong>{format_currency(peak_month['Revenue'])}</strong>. 
        November consistently shows 2-3x higher sales due to holiday shopping.
    </div>
    """, unsafe_allow_html=True)


def render_geographic_analysis(df: pd.DataFrame, metrics: dict):
    """Render geographic breakdown."""
    st.subheader("🌍 Revenue by Country")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Map or bar chart of top countries
        country_data = metrics['geographic']['country_data'].head(10)
        
        fig = px.bar(
            country_data,
            x='Revenue',
            y='Country',
            orientation='h',
            title=None,
            labels={'Revenue': 'Revenue (£)', 'Country': ''}
        )
        
        fig.update_traces(marker_color='#1f77b4')
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=400,
            margin=dict(l=100, r=50, t=30, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # UK vs International pie chart
        uk_int_data = pd.DataFrame({
            'Region': ['United Kingdom', 'International'],
            'Revenue': [
                metrics['geographic']['uk_revenue'],
                metrics['geographic']['international_revenue']
            ]
        })
        
        fig = px.pie(
            uk_int_data,
            values='Revenue',
            names='Region',
            title='UK vs International',
            color_discrete_sequence=['#1f77b4', '#ff7f0e']
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top 3 international markets
        st.markdown("**Top International Markets:**")
        intl = metrics['geographic']['country_data']
        intl = intl[intl['Country'] != 'United Kingdom'].head(3)
        for _, row in intl.iterrows():
            st.markdown(f"• {row['Country']}: {format_currency(row['Revenue'])}")

def render_customer_segments(df: pd.DataFrame):
    """Render RFM customer segmentation."""
    st.subheader("👥 Customer Segments (RFM Analysis)")

    df = df.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    # RFM table (per customer)
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    customer_stats = (
        df.groupby("Customer ID")
        .agg(
            Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
            Frequency=("Invoice", "nunique"),
            Monetary=("Revenue", "sum"),
        )
        .reset_index()
    )

    # R/F/M scores (1–5)
    customer_stats["R_Score"] = pd.qcut(
        customer_stats["Recency"], 5, labels=[5, 4, 3, 2, 1]
    ).astype(int)

    customer_stats["F_Score"] = pd.qcut(
        customer_stats["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    customer_stats["M_Score"] = pd.qcut(
        customer_stats["Monetary"], 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Segment rules (not equal-sized → realistic)
    def rfm_segment(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        if (r >= 4) and (f >= 4) and (m >= 4):
            return "Champions"
        if (r >= 3) and (f >= 4) and (m >= 3):
            return "Loyal"
        if (r >= 4) and (f <= 2):
            return "New Customers"
        if (r == 3) and (f >= 3) and (m >= 3):
            return "Potential Loyalists"
        if (r <= 2) and (f >= 3):
            return "At Risk"
        if (r <= 2) and (f <= 2):
            return "Hibernating"
        return "Need Attention"

    customer_stats["Segment"] = customer_stats.apply(rfm_segment, axis=1)

    # Keep the rest of your plotting logic the same (Customers + Revenue)
    segment_summary = customer_stats.groupby("Segment").agg({
        "Customer ID": "count",
        "Monetary": "sum"
    }).reset_index()
    segment_summary.columns = ["Segment", "Customers", "Revenue"]

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            segment_summary,
            x="Segment",
            y="Customers",
            title="Customers by Segment",
            color="Segment",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            segment_summary,
            x="Segment",
            y="Revenue",
            title="Revenue by Segment",
            color="Segment",
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Insight (no "top 25%" claim anymore)
    total_rev = segment_summary["Revenue"].sum()
    champions_rev = segment_summary.loc[segment_summary["Segment"] == "Champions", "Revenue"].sum()
    champions_cnt = segment_summary.loc[segment_summary["Segment"] == "Champions", "Customers"].sum()
    total_cnt = segment_summary["Customers"].sum()

    champ_rev_pct = (champions_rev / total_rev * 100) if total_rev else 0
    champ_cnt_pct = (champions_cnt / total_cnt * 100) if total_cnt else 0

    st.markdown(f"""
    <div class="insight-box">
        <strong>💡 Insight:</strong> <strong>Champions</strong> are ~<strong>{champ_cnt_pct:.0f}%</strong> of customers and generate
        ~<strong>{champ_rev_pct:.0f}%</strong> of total revenue. Focus retention efforts on this segment.
    </div>
    """, unsafe_allow_html=True)



def render_time_patterns(df: pd.DataFrame, metrics: dict):
    """Render time-based patterns."""
    st.subheader("⏰ Sales Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Day of week
        dow_data = metrics['time']['dow_data']
        
        fig = px.bar(
            dow_data,
            x='DayName',
            y='Revenue',
            title='Revenue by Day of Week',
            color='Revenue',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            showlegend=False,
            height=350,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Hour of day
        hour_data = metrics['time']['hourly_data']
        
        fig = px.line(
            hour_data,
            x='Hour',
            y='Revenue',
            title='Revenue by Hour of Day',
            markers=True
        )
        fig.update_traces(line_color='#ff7f0e')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    <div class="insight-box">
        <strong>💡 Insight:</strong> Peak sales occur on <strong>{metrics['time']['peak_day']}</strong> 
        at <strong>{metrics['time']['peak_hour']}:00</strong>. 
        Schedule marketing campaigns and promotions around these times.
    </div>
    """, unsafe_allow_html=True)

def render_cohort_retention(df: pd.DataFrame):
    """Render cohort retention heatmap (monthly)."""
    st.subheader("🧊 Cohort Retention (Monthly)")

    d = df.copy()
    d["InvoiceDate"] = pd.to_datetime(d["InvoiceDate"], errors="coerce")
    d = d.dropna(subset=["Customer ID", "InvoiceDate"])

    # Cohort month = first purchase month per customer
    first_purchase = (
        d.groupby("Customer ID")["InvoiceDate"]
        .min()
        .reset_index()
        .rename(columns={"InvoiceDate": "CohortDate"})
    )
    first_purchase["Cohort"] = first_purchase["CohortDate"].dt.to_period("M")

    d["TransactionMonth"] = d["InvoiceDate"].dt.to_period("M")
    d = d.merge(first_purchase[["Customer ID", "Cohort"]], on="Customer ID", how="left")

    # Months since first purchase
    d["CohortAge"] = (d["TransactionMonth"] - d["Cohort"]).apply(lambda x: x.n)

    # Count active customers by cohort + age
    cohort_counts = (
        d.groupby(["Cohort", "CohortAge"])["Customer ID"]
        .nunique()
        .reset_index(name="Customers")
    )

    # Pivot to matrix
    retention_matrix = (
        cohort_counts.pivot(index="Cohort", columns="CohortAge", values="Customers")
        .fillna(0)
        .sort_index()
    )

    # Convert to retention % (divide by month 0)
    if 0 not in retention_matrix.columns:
        st.info("Not enough data to compute cohort retention (missing cohort month 0).")
        return

    cohort_size = retention_matrix[0].replace(0, pd.NA)
    retention_pct = (retention_matrix.divide(cohort_size, axis=0) * 100).fillna(0).round(1)

    # Keep first N months so the chart stays readable
    max_months = min(12, retention_pct.shape[1])
    retention_pct = retention_pct.iloc[:, :max_months]

    # Make labels nicer
    retention_pct.index = retention_pct.index.astype(str)

    # Quick KPI
    avg_m1 = float(retention_pct[1].mean()) if 1 in retention_pct.columns else 0.0
    c1, c2, c3 = st.columns(3)
    c1.metric("Cohorts", int(retention_pct.shape[0]))
    c2.metric("Months tracked", int(retention_pct.shape[1] - 1))
    c3.metric("Avg Month-1 Retention", f"{avg_m1:.1f}%")

    # Heatmap
    fig = px.imshow(
        retention_pct,
        text_auto=True,
        aspect="auto",
        labels=dict(x="Months Since First Purchase", y="Cohort (First Purchase Month)", color="Retention %"),
        title="Customer Retention by Cohort (%)"
    )
    fig.update_layout(height=520)
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Retention = % of customers in each cohort who purchased again after N months.")


def render_top_products(df: pd.DataFrame):
    """Render top products analysis."""
    st.subheader("🏆 Top Products")
    
    product_stats = df.groupby(['StockCode', 'Description']).agg({
        'Revenue': 'sum',
        'Quantity': 'sum',
        'Invoice': 'nunique'
    }).reset_index()
    product_stats = product_stats.sort_values('Revenue', ascending=False).head(10)
    
    fig = px.bar(
        product_stats,
        x='Revenue',
        y='Description',
        orientation='h',
        title=None,
        labels={'Revenue': 'Revenue (£)', 'Description': ''}
    )
    
    fig.update_traces(marker_color='#2ca02c')
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=400,
        margin=dict(l=200, r=50, t=30, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_sidebar_filters(df: pd.DataFrame):
    """Render sidebar filters."""
    st.sidebar.header("🎛️ Filters")
    
    # Date range
    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Country filter
    countries = ['All'] + sorted(df['Country'].unique().tolist())
    selected_country = st.sidebar.selectbox("Country", countries)
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['InvoiceDate'].dt.date >= date_range[0]) &
            (filtered_df['InvoiceDate'].dt.date <= date_range[1])
        ]
    
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    
    # Show filter summary
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Filtered Data:**")
    st.sidebar.markdown(f"• {len(filtered_df):,} transactions")
    st.sidebar.markdown(f"• {filtered_df['Customer ID'].nunique():,} customers")
    st.sidebar.markdown(f"• {format_currency(filtered_df['Revenue'].sum())} revenue")
    
    return filtered_df


def main():
    """Main application."""
    
    # Header
    st.title("🛒 E-commerce Sales Dashboard")
    st.markdown("*Analyzing UK Online Retail Performance (2009-2011)*")
    st.markdown("---")
    
    # Load data
    df = get_data()
    
    # Apply filters
    filtered_df = render_sidebar_filters(df)
    
    # Calculate metrics
    metrics = {
        'revenue': calculate_revenue_metrics(filtered_df),
        'customers': calculate_customer_metrics(filtered_df),
        'geographic': calculate_geographic_metrics(filtered_df),
        'time': calculate_time_metrics(filtered_df)
    }
    
    # Render dashboard sections
    render_kpi_cards(metrics)
    
    st.markdown("---")
    
    # Main charts
    render_revenue_trend(filtered_df)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        render_customer_segments(filtered_df)
    with col2:
        render_top_products(filtered_df)
    
    st.markdown("---")
    
    render_geographic_analysis(filtered_df, metrics)
    
    st.markdown("---")
    
    render_time_patterns(filtered_df, metrics)

    st.markdown("---")
    render_cohort_retention(filtered_df)

    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>📊 Data Source: UCI Machine Learning Repository - Online Retail II Dataset</p>
        <p>Built with Streamlit • By Ashish Patel</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
