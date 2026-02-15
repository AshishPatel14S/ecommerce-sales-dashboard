# Customization Guide

## 5 Ways to Make This Project Your Own

This guide shows you how to customize the E-commerce Sales Dashboard to create a unique portfolio piece that stands out.

---

## 1. Focus on a Single Market

**What to change:** Filter the analysis to one country (Germany, France, or Netherlands)

**Why it's valuable:** Shows you can do deep-dive market analysis

**How to do it:**

```python
# In preprocessing.py, add a country filter
df = df[df['Country'] == 'Germany']

# Update the case study to focus on "German Market Analysis"
```

**New business questions to answer:**
- What products sell best in this market?
- Are there seasonal patterns specific to this country?
- What's the customer lifetime value for this market?

---

## 2. Add Product Category Analysis

**What to change:** Create product categories and analyze by category

**Why it's valuable:** Shows you can create taxonomy and derive insights from it

**How to do it:**

```python
# Create categories based on description keywords
def categorize_product(description):
    desc = str(description).lower()
    if 'bag' in desc or 'tote' in desc:
        return 'Bags'
    elif 'candle' in desc or 'holder' in desc:
        return 'Home Decor'
    elif 'christmas' in desc or 'xmas' in desc:
        return 'Seasonal'
    elif 'cup' in desc or 'mug' in desc:
        return 'Drinkware'
    else:
        return 'Other'

df['Category'] = df['Description'].apply(categorize_product)
```

**New insights to generate:**
- Category mix by country
- Seasonal category trends
- Category profitability analysis

---

## 3. Build a Cohort Retention Analysis

**What to change:** Track customer cohorts by first purchase month

**Why it's valuable:** Demonstrates understanding of retention metrics (key for SaaS/subscription companies)

**How to do it:**

```python
# Calculate first purchase date per customer
first_purchase = df.groupby('Customer ID')['InvoiceDate'].min().reset_index()
first_purchase.columns = ['Customer ID', 'CohortDate']
first_purchase['Cohort'] = first_purchase['CohortDate'].dt.to_period('M')

# Merge back to transactions
df = df.merge(first_purchase[['Customer ID', 'Cohort']], on='Customer ID')

# Calculate cohort metrics
df['TransactionMonth'] = df['InvoiceDate'].dt.to_period('M')
df['CohortAge'] = (df['TransactionMonth'] - df['Cohort']).apply(lambda x: x.n)

# Build retention matrix
cohort_data = df.groupby(['Cohort', 'CohortAge'])['Customer ID'].nunique().reset_index()
cohort_pivot = cohort_data.pivot(index='Cohort', columns='CohortAge', values='Customer ID')
retention = cohort_pivot.divide(cohort_pivot[0], axis=0) * 100
```

**New dashboard section:** Cohort heatmap showing retention over time

---

## 4. Add Demand Forecasting

**What to change:** Use Prophet or ARIMA to forecast future sales

**Why it's valuable:** Shows predictive modeling skills

**How to do it:**

```python
# Install: pip install prophet

from prophet import Prophet

# Prepare data for Prophet
daily_sales = df.groupby(df['InvoiceDate'].dt.date)['Revenue'].sum().reset_index()
daily_sales.columns = ['ds', 'y']

# Fit model
model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
model.fit(daily_sales)

# Forecast next 90 days
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)

# Plot
model.plot(forecast)
```

**New metrics to show:**
- Forecast accuracy (MAPE)
- Predicted revenue for next quarter
- Confidence intervals

---

## 5. Create an Executive Summary Report

**What to change:** Add automated PDF report generation

**Why it's valuable:** Shows you can communicate to non-technical stakeholders

**How to do it:**

```python
# Install: pip install fpdf2

from fpdf import FPDF
import matplotlib.pyplot as plt

class SalesReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Monthly Sales Executive Summary', 0, 1, 'C')
    
    def add_kpi_section(self, kpis):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Key Metrics', 0, 1)
        self.set_font('Arial', '', 11)
        for kpi, value in kpis.items():
            self.cell(0, 8, f'{kpi}: {value}', 0, 1)

# Generate report
pdf = SalesReport()
pdf.add_page()
pdf.add_kpi_section({
    'Total Revenue': '£9.75M',
    'Total Customers': '5,942',
    'YoY Growth': '+23%'
})
pdf.output('monthly_report.pdf')
```

**Add to dashboard:** "Download Report" button

---

## Combination Ideas

**For Data Analyst roles:**
- Customization 1 (Single Market) + 2 (Categories) + 5 (Executive Report)

**For Data Scientist roles:**
- Customization 3 (Cohort Analysis) + 4 (Forecasting)

**For Product/Growth roles:**
- Customization 3 (Cohort Analysis) + 2 (Categories)

---

## Quick Wins (Under 1 Hour Each)

1. **Change the color scheme** - Update Plotly colors to match a company you're targeting
2. **Add more filters** - Product category, order value ranges
3. **Create a "What-If" calculator** - "What if we increased retention by 5%?"
4. **Add data quality section** - Show missing values, outliers handled
5. **Include SQL queries** - Show equivalent SQL for key analyses

---

## Remember

The goal isn't to implement all 5 customizations. Pick ONE that:
- Aligns with your target role
- You can explain confidently in an interview
- Adds genuine analytical value

A focused, well-executed customization beats multiple half-finished additions.
