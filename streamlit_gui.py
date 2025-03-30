import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import time
import pytz  # Import pytz for timezone handling

REFRESH_INTERVAL_SECONDS = 10
DB_NAME = "energy_data.db"
TARGET_TIMEZONE = 'America/New_York'  # EST/EDT


def fetch_data(table_name):
    """Fetches data from the selected table."""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn, parse_dates=['timestamp'])
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching data from {table_name}: {e}")
        return None

def plot_data(df, table_name, time_col, value_col, target_timezone):
    """Plots the data using Matplotlib and converts the timezone."""
    try:
        # Set the time column as the index
        df.set_index(time_col, inplace=True)

        # Localize to UTC first (if not already) and then convert to the target timezone
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        df.index = df.index.tz_convert(target_timezone)

        # Sort the dataframe by the index (time)
        df.sort_index(inplace=True)

        # Plotting the data with matplotlib
        fig, ax = plt.subplots()
        ax.plot(df.index, df[value_col])
        ax.set_xlabel(time_col)
        ax.set_ylabel(value_col)
        ax.set_title(f"{value_col} vs {time_col} from {table_name} ({target_timezone})")
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.tight_layout()
        return fig  # Return the figure
    except Exception as e:
        st.error(f"Error plotting data from {table_name}: {e}")
        return None


def get_latest_balance():
    """Fetches the most recent balance value from the 'balance' table."""
    try:
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT value FROM balance ORDER BY timestamp DESC LIMIT 1"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            return df['value'].iloc[0]
        else:
            return None

    except Exception as e:
        st.error(f"Error fetching latest balance: {e}")
        return None

# Streamlit UI
st.title("Energy Monitoring Dashboard")

# Display the latest balance at the top
latest_balance = get_latest_balance()
if latest_balance is not None:
    st.markdown(f"**Latest Balance: {latest_balance:.2f} ETH**", unsafe_allow_html=True)  # Format as currency
else:
    st.warning("Could not retrieve latest balance.")

# Define table names and corresponding column names
tables_config = {
    "energy_production": {"time_col": "timestamp", "value_col": "value"},
    "energy_consumption": {"time_col": "timestamp", "value_col": "value"},
}

# Fetch and plot data for each table
for table_name, config in tables_config.items():
    df = fetch_data(table_name)
    if df is not None:
        fig = plot_data(df, table_name, config["time_col"], config["value_col"], TARGET_TIMEZONE)
        if fig is not None:
            st.pyplot(fig)  # Display the Matplotlib plot in Streamlit
    else:
        st.warning(f"Could not display graph for {table_name}.")

# --- Auto-refresh ---
time.sleep(REFRESH_INTERVAL_SECONDS)
st.rerun()