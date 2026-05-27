"""
Analysis Script
Generates key insights and visualizations from the e-commerce data.

Run: python src/analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('husl')


def load_data():
    """Load processed data."""
    project_root = Path(__file__).parent.parent
    
    # Try processed data first, fall back to sample
    processed_file = project_root / 'data' / 'processed' / 'cleaned_transactions.csv'
    sample_file = project_root / 'data' / 'sample' / 'sample_data.csv'
    
    if processed_file.exists():
        df = pd.read_csv(processed_file)
    elif sample_file.exists():
        df = pd.read_csv(sample_file)
    else:
        raise FileNotFoundError("No data found. Run preprocessing first.")
    
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    return df


def create_monthly_revenue_chart(df, save_path):
    """Create and save monthly revenue trend chart."""
    monthly = df.groupby(df['InvoiceDate'].dt.to_period('M'))['Revenue'].sum().reset_index()
    monthly['InvoiceDate'] = monthly['InvoiceDate'].astype(str)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.fill_between(range(len(monthly)), monthly['Revenue'], alpha=0.3, color='#1f77b4')
    ax.plot(range(len(monthly)), monthly['Revenue'], marker='o', color='#1f77b4', linewidth=2)
    
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly['InvoiceDate'], rotation=45, ha='right')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Revenue (£)', fontsize=12)
    ax.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold')
    
    # Add annotation for peak
    peak_idx = monthly['Revenue'].idxmax()
    peak_value = monthly.loc[peak_idx, 'Revenue']
    peak_month = monthly.loc[peak_idx, 'InvoiceDate']
    ax.annotate(f'Peak: £{peak_value:,.0f}\n({peak_month})', 
                xy=(peak_idx, peak_value),
                xytext=(peak_idx - 2, peak_value * 1.1),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   Saved: {save_path}")


def create_customer_segments_chart(df, save_path):
    """Create and save customer segmentation chart using proper RFM scoring."""
    reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

    customer_stats = df.groupby('Customer ID').agg(
        Recency=('InvoiceDate', lambda x: (reference_date - x.max()).days),
        Frequency=('Invoice', 'nunique'),
        Monetary=('Revenue', 'sum')
    ).reset_index()

    customer_stats['R_Score'] = pd.qcut(customer_stats['Recency'], q=5, labels=[5,4,3,2,1])
    customer_stats['F_Score'] = pd.qcut(customer_stats['Frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5])
    customer_stats['M_Score'] = pd.qcut(customer_stats['Monetary'].rank(method='first'), q=5, labels=[1,2,3,4,5])

    def segment_customer(row):
        r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'New Customers'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'Lost'
        else:
            return 'Potential Loyalists'

    customer_stats['Segment'] = customer_stats.apply(segment_customer, axis=1)

    segment_summary = customer_stats.groupby('Segment').agg(
        Customers=('Customer ID', 'count'),
        Revenue=('Monetary', 'sum')
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(segment_summary)))
    axes[0].bar(segment_summary['Segment'], segment_summary['Customers'], color=colors)
    axes[0].set_xlabel('Segment', fontsize=12)
    axes[0].set_ylabel('Number of Customers', fontsize=12)
    axes[0].set_title('Customers by RFM Segment', fontsize=14, fontweight='bold')
    axes[0].tick_params(axis='x', rotation=15)

    colors = plt.cm.Oranges(np.linspace(0.3, 0.9, len(segment_summary)))
    axes[1].bar(segment_summary['Segment'], segment_summary['Revenue'], color=colors)
    axes[1].set_xlabel('Segment', fontsize=12)
    axes[1].set_ylabel('Revenue (£)', fontsize=12)
    axes[1].set_title('Revenue by RFM Segment', fontsize=14, fontweight='bold')
    axes[1].tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   Saved: {save_path}")

    return segment_summary


def create_geographic_chart(df, save_path):
    """Create and save geographic distribution chart."""
    country_stats = df.groupby('Country')['Revenue'].sum().reset_index()
    country_stats = country_stats.sort_values('Revenue', ascending=True)
    
    # Top 10
    top_countries = country_stats.tail(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(top_countries['Country'], top_countries['Revenue'], color='#2ca02c')
    
    # Highlight UK
    uk_idx = top_countries[top_countries['Country'] == 'United Kingdom'].index
    if len(uk_idx) > 0:
        bar_idx = list(top_countries['Country']).index('United Kingdom')
        bars[bar_idx].set_color('#1f77b4')
    
    ax.set_xlabel('Revenue (£)', fontsize=12)
    ax.set_title('Top 10 Countries by Revenue', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   Saved: {save_path}")


def create_time_patterns_chart(df, save_path):
    """Create and save time patterns chart."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Day of week
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_stats = df.groupby('DayOfWeek')['Revenue'].sum().reset_index()
    dow_stats['DayName'] = dow_stats['DayOfWeek'].apply(lambda x: day_names[x])
    
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, 7))
    axes[0].bar(dow_stats['DayName'], dow_stats['Revenue'], color=colors)
    axes[0].set_xlabel('Day of Week', fontsize=12)
    axes[0].set_ylabel('Revenue (£)', fontsize=12)
    axes[0].set_title('Revenue by Day of Week', fontsize=14, fontweight='bold')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Hour of day
    hour_stats = df.groupby('Hour')['Revenue'].sum().reset_index()
    axes[1].plot(hour_stats['Hour'], hour_stats['Revenue'], marker='o', color='#ff7f0e', linewidth=2)
    axes[1].fill_between(hour_stats['Hour'], hour_stats['Revenue'], alpha=0.3, color='#ff7f0e')
    axes[1].set_xlabel('Hour of Day', fontsize=12)
    axes[1].set_ylabel('Revenue (£)', fontsize=12)
    axes[1].set_title('Revenue by Hour of Day', fontsize=14, fontweight='bold')
    axes[1].set_xticks(range(0, 24, 2))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   Saved: {save_path}")


def generate_summary_report(df, segment_summary):
    """Print summary statistics."""
    total_revenue = df['Revenue'].sum()
    total_customers = df['Customer ID'].nunique()
    total_orders = df['Invoice'].nunique()
    
    # Top 20% analysis
    customer_revenue = df.groupby('Customer ID')['Revenue'].sum().sort_values(ascending=False)
    top_20_count = int(len(customer_revenue) * 0.2)
    top_20_revenue = customer_revenue.head(top_20_count).sum()
    
    # Peak month
    monthly = df.groupby(df['InvoiceDate'].dt.to_period('M'))['Revenue'].sum()
    peak_month = monthly.idxmax()
    peak_revenue = monthly.max()
    avg_monthly = monthly.mean()
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"""
📈 REVENUE OVERVIEW
   Total Revenue: £{total_revenue:,.2f}
   Total Orders: {total_orders:,}
   Total Customers: {total_customers:,}
   Avg Order Value: £{total_revenue/total_orders:.2f}

📅 SEASONALITY
   Peak Month: {peak_month} (£{peak_revenue:,.2f})
   Avg Monthly Revenue: £{avg_monthly:,.2f}
   Peak vs Average: {peak_revenue/avg_monthly:.1f}x

👥 CUSTOMER VALUE
   Top 20% customers: {top_20_count}
   Revenue from top 20%: £{top_20_revenue:,.2f} ({top_20_revenue/total_revenue*100:.0f}%)

🌍 GEOGRAPHIC
   Countries: {df['Country'].nunique()}
   UK Revenue: £{df[df['Country']=='United Kingdom']['Revenue'].sum():,.2f}
""")


def main():
    """Run complete analysis."""
    print("🔄 Running e-commerce sales analysis...")
    
    # Setup
    project_root = Path(__file__).parent.parent
    img_dir = project_root / 'docs' / 'img'
    img_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    df = load_data()
    print(f"✅ Loaded {len(df):,} transactions")
    
    # Generate visualizations
    print("\n📊 Generating visualizations...")
    
    create_monthly_revenue_chart(df, img_dir / 'seasonal_trend.png')
    segment_summary = create_customer_segments_chart(df, img_dir / 'customer_segments.png')
    create_geographic_chart(df, img_dir / 'geographic.png')
    create_time_patterns_chart(df, img_dir / 'time_patterns.png')
    
    # Generate summary
    generate_summary_report(df, segment_summary)
    
    print("\n✅ Analysis complete! Charts saved to docs/img/")


if __name__ == '__main__':
    main()
