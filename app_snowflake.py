import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Load Snowflake configuration from Streamlit secrets
def get_secrets():
    """Retrieve Snowflake connection secrets."""
    config = st.secrets.get("snowflake", {})
    if not config:
        st.error("Secrets not loaded. Please check your secrets.toml file.")
    return config

# Configure Snowflake connection
def get_engine():
    config = get_secrets()
    if not config:
        return None
    engine_url = (
        f'snowflake://{config["user"]}:{config["password"]}@{config["account"]}/'
        f'{config["database"]}/{config["schema"]}?warehouse={config["warehouse"]}'
    )
    return create_engine(engine_url, echo=True)

# Load data from Snowflake and convert column names to uppercase
def load_data(query):
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()  # Return an empty DataFrame if there's an issue with the engine
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    df.columns = [col.upper() for col in df.columns]  # Convert to uppercase
    return df

# Function to transform wide-form data to long-form
def melt_data(df, id_vars, value_vars):
    # Ensure 'id_vars' are present in the DataFrame
    missing_id_vars = [var for var in id_vars if var not in df.columns]
    if missing_id_vars:
        raise KeyError(f"The following 'id_vars' are not present in the DataFrame: {missing_id_vars}")
    
    return df.melt(id_vars=id_vars, value_vars=value_vars, var_name='PRODUCT', value_name='SALES')

# Queries to get data
sales_daily_query = 'SELECT * FROM PHARMA_SALES_DB.SALES_DATA.TABLE_SALES_DAILY'
sales_hourly_query = 'SELECT * FROM PHARMA_SALES_DB.SALES_DATA.TABLE_SALES_HOURLY'
sales_monthly_query = 'SELECT * FROM PHARMA_SALES_DB.SALES_DATA.TABLE_SALES_MONTHLY'
sales_weekly_query = 'SELECT * FROM PHARMA_SALES_DB.SALES_DATA.TABLE_SALES_WEEKLY'

# Load datasets
sales_daily = load_data(sales_daily_query)
sales_hourly = load_data(sales_hourly_query)
sales_monthly = load_data(sales_monthly_query)
sales_weekly = load_data(sales_weekly_query)

# Set up the dashboard title
st.title('Pharma Sales Dashboard')

# Add a sub-description with the dataset source and GitHub repository link
st.markdown("""
This dashboard visualizes sales data from various time aggregations (daily, hourly, weekly, monthly) for pharmaceutical products.

The data is sourced from [Kaggle - Pharma Sales Data](https://www.kaggle.com/datasets/milanzdravkovic/pharma-sales-data/data).

For the source code and additional resources, visit the [GitHub repository](https://github.com/Donatopy/Pharma-Sales-Dashboard).
""")

# Sidebar for additional analysis
st.sidebar.header('Additional Analysis')

# Product selection for detailed analysis
product = st.sidebar.selectbox(
    'Select a product for detailed analysis:',
    sales_daily.columns.difference(['YEAR', 'MONTH', 'HOUR', 'WEEKDAY_NAME', 'DATUM'])
)

# Selection of the time aggregation level
option = st.sidebar.selectbox(
    'Select the time aggregation level:',
    ('Daily', 'Hourly', 'Weekly', 'Monthly')
)

# Product information in the sidebar
product_info = """
**M01AB** - Anti-inflammatory and antirheumatic products, non-steroids, Acetic acid derivatives and related substances  
**M01AE** - Anti-inflammatory and antirheumatic products, non-steroids, Propionic acid derivatives  
**N02BA** - Other analgesics and antipyretics, Salicylic acid and derivatives  
**N02BE/B** - Other analgesics and antipyretics, Pyrazolones and Anilides  
**N05B** - Psycholeptics drugs, Anxiolytic drugs  
**N05C** - Psycholeptics drugs, Hypnotics and sedatives drugs  
**R03** - Drugs for obstructive airway diseases  
**R06** - Antihistamines for systemic use
"""
# Highlight the selected product
highlighted_product_info = product_info.replace(product, f"<span style='color:red'>{product}</span>")
st.sidebar.markdown(highlighted_product_info, unsafe_allow_html=True)

st.sidebar.write("""
Sales data are resampled to hourly, daily, weekly, and monthly periods. The data has been pre-processed, including outlier detection, treatment, and missing data imputation.
""")

# Displaying sales data at the selected time level
st.write(f"Displaying sales data at the **{option}** level.")

# Filter and display data based on the selected option
if option == 'Daily':
    st.subheader('Daily Sales Overview')
    id_vars = ['DATUM']
    value_vars = sales_daily.columns.difference(['YEAR', 'MONTH', 'HOUR', 'WEEKDAY_NAME'])
    sales_data = melt_data(sales_daily, id_vars=id_vars, value_vars=value_vars)
elif option == 'Hourly':
    st.subheader('Hourly Sales Overview')
    id_vars = ['DATUM', 'HOUR']
    value_vars = sales_hourly.columns.difference(['YEAR', 'MONTH', 'HOUR', 'WEEKDAY_NAME'])
    sales_data = melt_data(sales_hourly, id_vars=id_vars, value_vars=value_vars)
elif option == 'Weekly':
    st.subheader('Weekly Sales Overview')
    id_vars = ['DATUM']
    value_vars = sales_weekly.columns.difference(['YEAR', 'MONTH', 'HOUR', 'WEEKDAY_NAME'])
    sales_data = melt_data(sales_weekly, id_vars=id_vars, value_vars=value_vars)
else:
    st.subheader('Monthly Sales Overview')
    id_vars = ['DATUM']
    value_vars = sales_monthly.columns.difference(['YEAR', 'MONTH', 'HOUR', 'WEEKDAY_NAME'])
    sales_data = melt_data(sales_monthly, id_vars=id_vars, value_vars=value_vars)

# Filter and display data for the selected product
if option == 'Daily':
    filtered_data = sales_daily[['DATUM', product]].rename(columns={product: 'SALES'})
elif option == 'Hourly':
    filtered_data = sales_hourly[['DATUM', 'HOUR', product]].rename(columns={product: 'SALES'})
elif option == 'Weekly':
    filtered_data = sales_weekly[['DATUM', product]].rename(columns={product: 'SALES'})
else:
    filtered_data = sales_monthly[['DATUM', product]].rename(columns={product: 'SALES'})

# Create and display the sales trend chart for the selected product
fig_prod = px.line(filtered_data, x='DATUM', y='SALES',
                   title=f'Sales Trend for {product}',
                   labels={'DATUM': 'Date', 'SALES': 'Sales Amount'},
                   color_discrete_sequence=px.colors.qualitative.Plotly)

fig_prod.update_layout(
    xaxis_title='Date',
    yaxis_title='Sales Amount',
    title_x=0.5,
    title_font_size=24,
    xaxis_tickformat='%Y-%m-%d',
    template='plotly_dark'
)

st.plotly_chart(fig_prod)

# Create and display the main sales trend chart
fig = px.line(sales_data, x='DATUM', y='SALES', color='PRODUCT',
              title=f'Sales Trend ({option})',
              labels={'DATUM': 'Date', 'SALES': 'Sales Amount'},
              color_discrete_sequence=px.colors.qualitative.Plotly)

fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Sales Amount',
    legend_title='Product',
    template='plotly_dark',
    title_x=0.5,
    title_font_size=24,
    xaxis_tickformat='%Y-%m-%d'
)

st.plotly_chart(fig)

# Additional Graphs

# 1. Comparative Bar Chart
st.subheader('Comparative Sales by Product')
sales_data_comparative = sales_data.groupby('PRODUCT').agg({'SALES': 'sum'}).reset_index()
fig_comparative = px.bar(sales_data_comparative, x='PRODUCT', y='SALES',
                        title='Comparison of Sales by Product',
                        labels={'PRODUCT': 'Product', 'SALES': 'Sales'},
                        color='SALES', color_continuous_scale=px.colors.sequential.Plasma)
fig_comparative.update_layout(
    xaxis_title='Product',
    yaxis_title='Sales',
    title_x=0.5,
    title_font_size=24,
    template='plotly_dark'
)
st.plotly_chart(fig_comparative)

# 2. Annual Trends Line Chart
st.subheader('Annual Sales Trends')
sales_data['YEAR'] = pd.to_datetime(sales_data['DATUM']).dt.year
sales_annual = sales_data.groupby(['YEAR', 'PRODUCT']).agg({'SALES': 'sum'}).reset_index()
fig_annual = px.line(sales_annual, x='YEAR', y='SALES', color='PRODUCT',
                     title='Annual Sales Trends',
                     labels={'YEAR': 'Year', 'SALES': 'Sales'},
                     color_discrete_sequence=px.colors.qualitative.Plotly)
fig_annual.update_layout(
    xaxis_title='Year',
    yaxis_title='Sales',
    title_x=0.5,
    title_font_size=24,
    template='plotly_dark'
)
st.plotly_chart(fig_annual)

# 3. Sales Distribution Histogram
st.subheader('Sales Distribution Histogram')
fig_histogram = px.histogram(sales_data, x='SALES',
                             title='Sales Distribution',
                             labels={'SALES': 'Sales'},
                             color_discrete_sequence=px.colors.qualitative.Plotly)
fig_histogram.update_layout(
    xaxis_title='Sales',
    yaxis_title='Frequency',
    title_x=0.5,
    title_font_size=24,
    template='plotly_dark'
)
st.plotly_chart(fig_histogram)
