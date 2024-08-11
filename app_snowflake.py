import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

def get_engine():
    """Create and return a SQLAlchemy engine."""
    config = st.secrets.get("snowflake")
    if not config:
        st.error("Snowflake configuration not found.")
        return None
    
    st.write(f"Config: {config}")  # Debugging line
    engine_url = (
        f'snowflake://{config["user"]}:{config["password"]}@{config["account"]}/'
        f'{config["database"]}/{config["schema"]}?warehouse={config["warehouse"]}'
    )
    st.write(f"Engine URL: {engine_url}")  # Debugging line

    try:
        engine = create_engine(engine_url, echo=True)
        return engine
    except Exception as e:
        st.error(f"Error creating engine: {e}")
        return None

def load_data(query):
    """Load data from Snowflake into a pandas DataFrame."""
    engine = get_engine()
    if not engine:
        st.error("Failed to create engine.")
        return pd.DataFrame()  # Return an empty DataFrame if engine creation failed

    try:
        with engine.connect() as conn:
            st.write(f"Executing query: {query}")  # Debugging line
            df = pd.read_sql(query, conn)
        df.columns = [col.upper() for col in df.columns]  # Convert to uppercase
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

# Test the connection
def test_connection():
    """Test Snowflake connection."""
    config = st.secrets.get("snowflake")
    if not config:
        st.error("Snowflake configuration not found.")
        return
    
    engine_url = (
        f'snowflake://{config["user"]}:{config["password"]}@{config["account"]}/'
        f'{config["database"]}/{config["schema"]}?warehouse={config["warehouse"]}'
    )
    try:
        engine = create_engine(engine_url, echo=True)
        with engine.connect() as conn:
            st.write("Connection successful")
            result = conn.execute("SELECT CURRENT_DATE;")
            st.write(result.fetchone())
    except Exception as e:
        st.error(f"Error testing connection: {e}")

test_connection()

# Define queries
sales_daily_query = 'SELECT * FROM PHARMA_SALES_DB.SALES_DATA.TABLE_SALES_DAILY'
sales_hourly_query = 'SELECT * FROM PHARMA_SALES_DB.SALES_DATA.TABLE_SALES_HOURLY'
sales_monthly_query = 'SELECT * FROM PHARMA_SALES_DB.SALES_DATA.TABLE_SALES_MONTHLY'
sales_weekly_query = 'SELECT * FROM PHARMA_SALES_DB.SALES_DATA.TABLE_SALES_WEEKLY'

# Load datasets
sales_daily = load_data(sales_daily_query)
sales_hourly = load_data(sales_hourly_query)
sales_monthly = load_data(sales_monthly_query)
sales_weekly = load_data(sales_weekly_query)
