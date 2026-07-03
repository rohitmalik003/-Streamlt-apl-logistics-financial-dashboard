import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page layout configuration
st.set_page_config(page_title="APL Logistics Business Intelligence Dashboard", layout="wide")
st.title("📊 APL Logistics Financial Performance Dashboard")
st.markdown("---")

# Load the optimized dashboard file generated from Colab
@st.cache_data
def load_dashboard_data():
    return pd.read_csv("cleaned_APL_Logistics.csv.gz")

df = load_dashboard_data()

# ==========================================
# GLOBAL SIDEBAR FILTERS (UPDATED)
# ==========================================
st.sidebar.header("Global Filters")

# 1. Market & Region Dropdowns
selected_market = st.sidebar.multiselect("Filter by Market Location", options=df['Market'].unique(), default=df['Market'].unique())
sub_region_options = df[df['Market'].isin(selected_market)]['Order Region'].unique() if selected_market else df['Order Region'].unique()
selected_region = st.sidebar.multiselect("Filter by Order Region", options=sub_region_options, default=sub_region_options)

# 2. Customer Segment Filter
# Checking if 'Customer Segment' exists in processed dataframe; falls back to 'Value Tier' if column was omitted during compression
segment_col = 'Customer Segment' if 'Customer Segment' in df.columns else 'Value Tier'
selected_segment = st.sidebar.multiselect("Filter by Segment/Tier", options=df[segment_col].unique(), default=df[segment_col].unique())

# 3. Category & Product Selector
selected_category = st.sidebar.multiselect("Filter by Category Name", options=df['Category Name'].unique(), default=df['Category Name'].unique())
sub_product_options = df[df['Category Name'].isin(selected_category)]['Product Name'].unique() if selected_category else df['Product Name'].unique()
selected_product = st.sidebar.multiselect("Filter by Product Name", options=sub_product_options, default=sub_product_options)

# 4. Discount Rate Slider
min_disc, max_disc = float(df['Order Item Discount Rate'].min()), float(df['Order Item Discount Rate'].max())
selected_disc_range = st.sidebar.slider("Filter by Order Discount Rate Range", min_value=min_disc, max_value=max_disc, value=(min_disc, max_disc), step=0.01)

# Apply All Filters Systematically to Dataframe
filtered_df = df[
    (df['Market'].isin(selected_market)) &
    (df['Order Region'].isin(selected_region)) &
    (df[segment_col].isin(selected_segment)) &
    (df['Category Name'].isin(selected_category)) &
    (df['Product Name'].isin(selected_product)) &
    (df['Order Item Discount Rate'] >= selected_disc_range[0]) &
    (df['Order Item Discount Rate'] <= selected_disc_range[1])
]

# ==========================================
# MODULE 1: REVENUE & PROFIT OVERVIEW
# ==========================================
st.header("📈 1. Financial Performance Overview")

# Global KPIs
total_sales = filtered_df['Sales'].sum()
total_prof = filtered_df['Order Profit Per Order'].sum()
margin = (total_prof / total_sales) * 100 if total_sales > 0 else 0

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
kpi_col1.metric("Total Revenue", f"${total_sales:,.2f}")
kpi_col2.metric("Total Profit", f"${total_prof:,.2f}")
kpi_col3.metric("Overall Profit Margin", f"{margin:.2f}%")

st.markdown("#### Regional Revenue vs Profit Insights")
# Region breakdown aggregation
region_data = filtered_df.groupby('Order Region').agg(
    Revenue=('Sales', 'sum'),
    Profit=('Order Profit Per Order', 'sum')
).reset_index().sort_values(by='Revenue', ascending=False)

fig_region = px.bar(
    region_data, x='Order Region', y=['Revenue', 'Profit'],
    barmode='group', title="Revenue vs. Net Profit Concentration Across Order Regions",
    labels={'value': 'Amount ($)', 'variable': 'Metric'},
    color_discrete_sequence=['#2b5c8f', '#2ca02c']
)
st.plotly_chart(fig_region, use_container_width=True)

st.markdown("---")

# ==========================================
# MODULE 2: CUSTOMER VALUE DASHBOARD
# ==========================================
st.header("👥 2. Customer Contribution & Value Index")

customer_agg = filtered_df.groupby('Customer Id').agg(
    Total_Sales=('Sales', 'sum'),
    Customer_Value_Index=('Order Profit Per Order', 'sum')
).reset_index()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 High-Value Customers (By Profit)")
    top_cust = customer_agg.sort_values(by='Customer_Value_Index', ascending=False).head(10)
    top_cust['Customer Id'] = top_cust['Customer Id'].astype(str)
    fig_top = px.bar(top_cust, x='Customer_Value_Index', y='Customer Id', orientation='h',
                     color='Customer_Value_Index', color_continuous_scale='Greens')
    st.plotly_chart(fig_top, use_container_width=True)
    
with col2:
    st.subheader("Top 10 Loss-Making Customers")
    bottom_cust = customer_agg.sort_values(by='Customer_Value_Index', ascending=True).head(10)
    bottom_cust['Customer Id'] = bottom_cust['Customer Id'].astype(str)
    fig_bottom = px.bar(bottom_cust, x='Customer_Value_Index', y='Customer Id', orientation='h',
                        color='Customer_Value_Index', color_continuous_scale='Reds_r')
    st.plotly_chart(fig_bottom, use_container_width=True)

st.subheader("Value Tier Distribution Segment Analysis")
tier_data = filtered_df.groupby('Value Tier').agg(
    Total_Sales=('Sales', 'sum'),
    Total_Profit=('Order Profit Per Order', 'sum'),
    Transaction_Count=('Sales', 'count')
).reset_index()
st.dataframe(tier_data.style.format({'Total_Sales': '${:,.2f}', 'Total_Profit': '${:,.2f}', 'Transaction_Count': '{:,}'}))

st.markdown("---")

# ==========================================
# MODULE 3: PRODUCT & CATEGORY PERFORMANCE
# ==========================================
st.header("📦 3. Product Portfolio & Category Diagnostics")

# Compute Category Margin Metrics
cat_data = filtered_df.groupby('Category Name').agg(
    Revenue=('Sales', 'sum'),
    Profit=('Order Profit Per Order', 'sum')
).reset_index()
cat_data['Category Margin (%)'] = (cat_data['Profit'] / cat_data['Revenue']) * 100
cat_data = cat_data.sort_values(by='Category Margin (%)', ascending=False)

st.subheader("Category Performance & Heatmap View")
fig_cat = px.density_heatmap(
    cat_data, x="Category Name", y="Category Margin (%)", z="Revenue",
    title="Category Heatmap: Margin vs Revenue Scaling Size",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig_cat, use_container_width=True)

st.subheader("Strategic Warning: High Revenue but Low Margin Products")
prod_data = filtered_df.groupby('Product Name').agg(
    Revenue=('Sales', 'sum'),
    Profit=('Order Profit Per Order', 'sum')
).reset_index()
prod_data['Product Margin (%)'] = (prod_data['Profit'] / prod_data['Revenue']) * 100

avg_margin = prod_data['Product Margin (%)'].mean()
high_rev_low_marg = prod_data[prod_data['Product Margin (%)'] < avg_margin].sort_values(by='Revenue', ascending=False).head(10)
st.dataframe(high_rev_low_marg.style.format({'Revenue': '${:,.2f}', 'Profit': '${:,.2f}', 'Product Margin (%)': '{:.2f}%'}))

st.markdown("---")

# ==========================================
# MODULE 4: DISCOUNT IMPACT ANALYZER
# ==========================================
st.header("🛑 4. Discount Impact & Strategic Scenarios")

# Core Diagnostics
disc_summary = filtered_df.groupby('Has_Discount').agg(
    Revenue=('Sales', 'sum'),
    Profit=('Order Profit Per Order', 'sum')
).reset_index()
disc_summary['Margin (%)'] = (disc_summary['Profit'] / disc_summary['Revenue']) * 100

st.subheader("Margin Degradation Analysis")
st.dataframe(disc_summary.style.format({'Revenue': '${:,.2f}', 'Profit': '${:,.2f}', 'Margin (%)': '{:.2f}%'}))

# What-If Modeling Segment
st.markdown("#### 🧮 'What-If' Simulation Model")
st.write("Simulate adjustments to current discounting logic to see changes to bottom line profitability.")

discount_cut = st.slider("Reduce existing discount rates across orders by (%):", min_value=0, max_value=100, value=20, step=5)

# Simulation Logic
simulated_df = filtered_df.copy()
# Compute recovered profit from reducing discount rates
reduction_factor = discount_cut / 100.0
simulated_df['Simulated_Profit'] = simulated_df['Order Profit Per Order'] + (simulated_df['Order Item Discount'] * reduction_factor)

orig_total_profit = filtered_df['Order Profit Per Order'].sum()
sim_total_profit = simulated_df['Simulated_Profit'].sum()
profit_lift = sim_total_profit - orig_total_profit

col_sim1, col_sim2, col_sim3 = st.columns(3)
col_sim1.metric("Original Profit", f"${orig_total_profit:,.2f}")
col_sim2.metric("Simulated Net Profit", f"${sim_total_profit:,.2f}", delta=f"${profit_lift:,.2f}")
col_sim3.metric("Simulated Margin", f"{(sim_total_profit / simulated_df['Sales'].sum()) * 100:.2f}%")

st.markdown("---")

# ==========================================
# NEW SECTION: PROJECT SUMMARY & REFLECTION
# ==========================================
st.header("📝 Project Retrospective: Challenges, Tasks & Technical Summary")

st.markdown("""
### 🔍 Project Context & Executed Tasks
The goal of this project was to establish an end-to-end analytics and forecasting pipeline for **APL Logistics** to evaluate revenue leaks, target logistical inefficiencies, and study how current promotional structures impact real profitability. 

The core operations carried out during this project include:
1. **Financial Validation & Cleanup:** Auditing transactional metrics to filter out statistical anomalies and business-crippling structural inconsistencies.
2. **Customer Segmentation Tiers:** Isolating top-tier brand champions from high-volume, net loss-making commercial accounts using a dynamic *Customer Value Index*.
3. **Product & Category Diagnostic Mapping:** Auditing the product line to flag high-volume items suffering from thin margins due to overhead costs.
4. **Predictive Risk Assessment:** Building standalone Machine Learning pipelines in Google Colab to gauge delivery and delay factors before they impact client relationships.

---

### ⚠️ Technical Challenges & Engineering Solutions

* **The Special Characters Encoding Problem:**
  * *Challenge:* The raw data contained international geographic labels, cities, and specific accent marks that caused immediate standard `utf-8` decoding failures during initialization.
  * *Solution:* Resolved by implementing a text-fallback mechanism using byte-resilient `latin1` encoding profiles during the Pandas parsing sequence.
  
* **Target Leakage Risks in Machine Learning Modeling:**
  * *Challenge:* When engineering predictors for shipping delay risk, columns like actual shipment times and downstream delivery status flags created target leakage, synthetically inflating model validation metrics to an unrealistic 100% accuracy.
  * *Solution:* Identified and dropped leaky post-transaction columns during Phase 1 preprocessing to ensure the model makes predictions using true upstream supply chain information.
  
* **Streamlit Runtime Lag & Refresh Delays:**
  * *Challenge:* Running multi-layered data cleaning logic, categorical matrix encodings, and string operations in real-time within the Streamlit code block degraded UI performance on interactive steps.
  * *Solution:* Structured a decoupled execution system where intensive financial pruning and feature narrowing are pre-computed in Google Colab, feeding a highly optimized, streamlined `.csv` payload into the visualization app.

---

### 🛠️ Technology Stack & Tools Used
* **Data Engineering & Preparation:** `Python`, `Pandas`, and `NumPy` for operational filters, categorical encoding transformation loops, and numerical cleaning matrix operations.
* **Predictive Frameworks:** `Scikit-Learn` utilizing balanced `RandomForestClassifier` configurations and robust scaling modules to address variable variance.
* **Interactive Visualization Suite:** `Streamlit Web Server Engine` combined with `Plotly Express` and `Plotly Graph Objects` to provide rich, interactive visualizations without performance lag.
""")
