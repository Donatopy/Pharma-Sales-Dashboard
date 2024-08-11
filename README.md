# Pharma Sales Dashboard

## Overview
The Pharma Sales Dashboard is an interactive Streamlit application designed to provide insights into pharmaceutical sales data. The dashboard utilizes various visualizations to help users analyze sales trends, product performance, and distribution of sales over different time periods.

The data used for this dashboard is sourced from Kaggle. You can explore the dataset [here](https://www.kaggle.com/datasets/milanzdravkovic/pharma-sales-data/data).

You can also access the live dashboard [here](https://pharma-sales-dashboard.streamlit.app/).

## Features
- **Sales Trend by Product**: Line chart showing the sales trend for selected products over time.
- **Comparative Sales by Product**: Bar chart comparing total sales across different products.
- **Annual Sales Trends**: Line chart illustrating the sales trends on an annual basis.
- **Sales Distribution Histogram**: Histogram displaying the distribution of sales amounts.
  
## Prerequisites
Before running the dashboard, ensure you have the following installed:

- **Python 3.7 or later**
- **Streamlit**
- **Pandas**
- **Plotly**
- **SQLAlchemy**
- **Snowflake SQLAlchemy**
- **Snowflake Connector for Python**

You can install the required Python packages using pip:

```bash
pip install streamlit pandas plotly sqlalchemy snowflake-sqlalchemy snowflake-connector-python
