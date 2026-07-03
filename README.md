# APL Logistics Financial Performance Dashboard

An end-to-end data pipeline and dynamic business intelligence web application designed for **APL Logistics** to isolate revenue leaks, track regional profit concentration, and simulate promotional margin recovery.

 Architecture & Features

*   Data Pipeline (`Google Colab`): Cleans, type-validates, and optimizes raw data  into a high-performance payload cleaned data.
*   Interactive UI (`Streamlit`): A single-page, scroll-down dashboard that eliminates tab latency.
*   Global Filters: Sidebar selectors for Market, Region, Customer Segment, Categories, Products, and Discount Rates.
*   Analytical Modules:
    1.  Financial Performance: Macro KPI tracking and Regional Revenue vs. Profit mapping.
    2.  Customer Value Dashboard: Top 10 profitable vs. bottom 10 loss-making accounts alongside value tier summaries.
    3.  Product Portfolio Diagnostics: Margin vs. Revenue density heatmaps and underperforming product warnings.
    4.  Strategic "What-If" Simulator: Interactive slider to reduce active discount rates (0–100%) and instantly project simulated profit lift and margin recovery.

 Engineering Retrospective
*   Encoding Fix: Solved international character parsing errors by deploying a byte-resilient `latin1` reader.
*   Target Leakage Prevention: Removed post-transaction delivery flags during preprocessing to protect the forecasting integrity of the machine learning pipeline.
*   Frontend Optimization: Pre-computed all heavy aggregations within Google Colab to deliver an instantaneous front-end response in Streamlit
