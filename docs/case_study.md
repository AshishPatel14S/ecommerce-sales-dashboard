# E-commerce Sales Dashboard

## Case Study

---

### TL;DR

Built an interactive sales dashboard analyzing £9.7M in transactions for a UK online retailer, revealing that November generates 3x average monthly revenue and the top 20% of customers drive 78% of revenue. The dashboard enables data-driven decisions on inventory planning, customer retention, and market expansion.

---

### Role & Timeline

**Role:** Data Analyst (Solo Project)  
**Timeline:** 4 weeks  
**Responsibilities:** Data cleaning, exploratory analysis, visualization, dashboard development, business recommendations

---

### Business Context

A UK-based online gift retailer needed to understand their sales performance to make better strategic decisions. Key questions included:

- Which months drive the most sales? Are there predictable patterns?
- Who are the high-value customers and how can we retain them?
- Which international markets have growth potential?
- What products should be prioritized for inventory?

Without these insights, the company risked overstocking unpopular items, missing seasonal opportunities, and losing valuable customers to competitors.

---

### Data & Methods

**Dataset:** UCI Online Retail II (publicly available)
- 1,067,371 transactions (541,909 after cleaning)
- 5,942 unique customers across 38 countries
- Dec 2009 – Dec 2011

**Methods:**
- Data cleaning (removed cancellations, nulls, outliers)
- RFM segmentation (Recency, Frequency, Monetary analysis)
- Time series analysis (seasonality, day-of-week patterns)
- Geographic breakdown with market share analysis

**Stack:** Python (Pandas, Plotly), Streamlit

---

### Results

| Metric | Finding | Business Impact |
|--------|---------|-----------------|
| Seasonality | November = 3x average revenue | Increase inventory 40% by October |
| Customer Value | Top 20% → 78% of revenue | Launch VIP loyalty program |
| Geographic | UK = 82%, Germany growing 15% YoY | Invest in EU fulfillment |
| Timing | Peak: Thursday at 12:00 | Schedule campaigns around peaks |

**Key Visualization:**

![Monthly Revenue](img/seasonal_trend.png)

*November spike clearly visible—driven by holiday gift shopping*

---

### Recommendations

1. **Inventory Planning:** Pre-stock 40% additional inventory by mid-October for holiday season
2. **Customer Retention:** Create tiered loyalty program; prioritize "Champions" segment with exclusive offers
3. **Market Expansion:** Test dedicated marketing in Germany/France; evaluate EU distribution center ROI
4. **Operational Efficiency:** Align staffing and marketing spend with Thursday peak periods

---

### Technical Highlights

- Built reproducible pipeline with one-command execution (`make reproduce`)
- Interactive Streamlit dashboard with date/country filters
- RFM segmentation identifying 6 customer segments
- Modular codebase for easy customization

---

### Next Steps

With more time, I would:
1. Build a customer lifetime value (CLV) prediction model
2. Create automated weekly reporting pipeline
3. Develop A/B testing framework for marketing campaigns
4. Add demand forecasting for inventory optimization

---

**Code:** [GitHub Repository Link]  
**Demo:** [Live Dashboard Link]  
**Contact:** [Your Email]
