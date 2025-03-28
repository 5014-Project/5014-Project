import streamlit as st
import sqlite3
import pandas as pd
import time
import datetime as dt
import requests 
import json     

# --- Configuration ---
DB_NAME = "energy_data.db"
REFRESH_INTERVAL_SECONDS = 10
DEFAULT_HISTORY_MINUTES = 60
# --- NEW: GUIAgent Web Endpoint ---
GUI_AGENT_URL = f"http://localhost:{9099}" # Match port in GUIAgent
STRATEGY_ENDPOINT = f"{GUI_AGENT_URL}/set_strategy"
# ---

# --- Database Functions ---
# ... (connect_db and fetch_recent_data remain the same - ensure fetch_recent_data handles 'trade_summary') ...
@st.cache_resource
def connect_db():
    try: return sqlite3.connect(f"file:{DB_NAME}?mode=ro", uri=True, check_same_thread=False)
    except Exception as e: st.error(f"DB Connect Error: {e}"); return None

@st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
def fetch_recent_data(_conn, table_name, minutes_back, parse_dates_col=None, index_col=None):
    if _conn is None: return pd.DataFrame()
    now_unix = time.time()
    start_time_unix = now_unix - (minutes_back * 60)
    try:
        query = f"SELECT * FROM {table_name} WHERE timestamp >= ? ORDER BY timestamp ASC"
        df = pd.read_sql_query(query, _conn, params=(start_time_unix,))
        if not df.empty and parse_dates_col and parse_dates_col in df.columns:
            df['datetime'] = pd.to_datetime(df[parse_dates_col], unit='s').dt.tz_localize(None)
            if index_col == 'datetime': df = df.set_index('datetime')
        return df
    except (pd.errors.DatabaseError, sqlite3.OperationalError) as e:
        st.warning(f"Data Fetch Warning ({table_name}): {e}")
        cols_map = {
            "blockchain_log": ['id', 'timestamp', 'agent_account', 'event_type', 'energy_kwh', 'price_eth', 'balance_eth', 'counterparty_address', 'status', 'auction_id'],
            "energy_production": ['id', 'timestamp', 'value'],
            "energy_consumption": ['id', 'timestamp', 'value'],
            "predictions": ['id', 'timestamp', 'predicted_demand', 'predicted_production'],
            "demand_response_log": ['id', 'timestamp', 'grid_predicted_demand', 'grid_predicted_supply', 'energy_rate_per_kwh', 'curtailment_kw'],
            "trade_summary": ['id', 'timestamp', 'total_energy_bought_kwh', 'total_energy_sold_kwh']
        }
        cols = cols_map.get(table_name, [])
        if cols:
            empty_df = pd.DataFrame(columns=[col for col in cols if col != 'datetime'])
            empty_df['datetime'] = pd.to_datetime([])
            if index_col == 'datetime': return empty_df.set_index('datetime')
            return empty_df
        return pd.DataFrame()
    except Exception as e: st.error(f"Unexpected Data Fetch Error ({table_name}): {e}"); return pd.DataFrame()

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="Smart Home Energy Dashboard")
st.title("⚡ Smart Home Energy & Blockchain Dashboard")
st.caption(f"Visualizing data from `{DB_NAME}`. Refreshing approx. every {REFRESH_INTERVAL_SECONDS} seconds.")

# Initialize session state for strategy
if 'current_ui_strategy' not in st.session_state:
    st.session_state['current_ui_strategy'] = 'neutral' # Default on first load

conn = connect_db()

if conn:
    # --- Sidebar ---
    st.sidebar.header("⚙️ Controls")
    history_minutes = st.sidebar.slider("Time Window (Minutes)", 5, 1440, DEFAULT_HISTORY_MINUTES, 5)

    # --- NEW: Strategy Selection ---
    st.sidebar.subheader("Trading Strategy")
    strategy_options = ["conservative", "neutral", "aggressive"]
    # Use st.session_state to keep track of the selection
    selected_strategy = st.sidebar.radio(
        "Set Negotiation Agent Strategy:",
        options=strategy_options,
        index=strategy_options.index(st.session_state.current_ui_strategy), # Set default index based on state
        key="strategy_radio" # Assign a key for stability
    )

    # Check if the selection changed and update the agent if necessary
    if selected_strategy != st.session_state.current_ui_strategy:
        st.session_state.current_ui_strategy = selected_strategy # Update state first
        payload = json.dumps({"strategy": selected_strategy})
        headers = {'Content-Type': 'application/json'}
        status_placeholder = st.sidebar.empty() # To show status messages
        try:
            status_placeholder.info(f"Attempting to set strategy to {selected_strategy}...")
            response = requests.post(STRATEGY_ENDPOINT, data=payload, headers=headers, timeout=5) # Add timeout
            response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
            # Check response content if needed
            # response_data = response.json()
            status_placeholder.success(f"✅ Strategy set to {selected_strategy}!")
            time.sleep(1.5) # Briefly show success message
            status_placeholder.empty() # Clear message
        except requests.exceptions.ConnectionError:
             status_placeholder.error(f"❌ Connection Error: Could not reach GUIAgent at {GUI_AGENT_URL}. Is it running?")
        except requests.exceptions.Timeout:
            status_placeholder.error("❌ Timeout: GUIAgent did not respond.")
        except requests.exceptions.RequestException as e:
             status_placeholder.error(f"❌ Failed to set strategy: {e}")
             try:
                 # Try to get more detail from agent's response
                 error_detail = e.response.json().get("message", "No details")
                 st.sidebar.caption(f"Agent Error: {error_detail}")
             except: pass # Ignore errors getting details
    # --- END Strategy Selection ---


    if st.sidebar.button("🔄 Refresh Now"): st.cache_data.clear(); st.rerun()

    # --- Fetch Data --- (Ensure fetch_recent_data handles trade_summary)
    df_prod = fetch_recent_data(conn, "energy_production", history_minutes, 'timestamp', 'datetime')
    df_cons = fetch_recent_data(conn, "energy_consumption", history_minutes, 'timestamp', 'datetime')
    df_blockchain = fetch_recent_data(conn, "blockchain_log", history_minutes, 'timestamp')
    df_preds = fetch_recent_data(conn, "predictions", history_minutes, 'timestamp', 'datetime')
    df_dr = fetch_recent_data(conn, "demand_response_log", history_minutes, 'timestamp', 'datetime')
    df_summary_latest = fetch_recent_data(conn, "trade_summary", history_minutes * 2)
    if not df_summary_latest.empty: df_summary_latest = df_summary_latest.sort_values(by='timestamp', ascending=False).iloc[[0]]

    # --- KPIs --- (Uses updated trade summary logic)
    st.header("📊 Live Metrics")
    kpi_cols = st.columns(9)
    # Traded Energy KPIs
    latest_bought = df_summary_latest['total_energy_bought_kwh'].iloc[0] if not df_summary_latest.empty else 0
    latest_sold = df_summary_latest['total_energy_sold_kwh'].iloc[0] if not df_summary_latest.empty else 0
    net_traded = latest_sold - latest_bought
    with kpi_cols[0]: st.metric(label="🛒 Energy Bought (kWh)", value=f"{latest_bought:.2f}", help="Total energy bought via auctions.")
    with kpi_cols[1]: st.metric(label="💰 Energy Sold (kWh)", value=f"{latest_sold:.2f}", help="Total energy sold via auctions.")
    with kpi_cols[2]:
        delta_val = f"{abs(net_traded):.2f}"; delta_text = "Balanced"; delta_color="off"
        if net_traded > 0: delta_text = f"{delta_val} (Net Sold)"; delta_color="normal"
        elif net_traded < 0: delta_text = f"{delta_val} (Net Bought)"; delta_color="inverse"
        st.metric(label="⚖️ Net Traded (kWh)", value=f"{net_traded:.2f}", delta=delta_text, delta_color=delta_color)
    # Prediction KPIs
    latest_pred_prod = df_preds['predicted_production'].iloc[-1] if not df_preds.empty else 0
    latest_pred_demand = df_preds['predicted_demand'].iloc[-1] if not df_preds.empty else 0
    with kpi_cols[3]: st.metric(label="📈 Pred. Prod (kW)", value=f"{latest_pred_prod:.2f}")
    with kpi_cols[4]: st.metric(label="📉 Pred. Demand (kW)", value=f"{latest_pred_demand:.2f}")
    # Demand Response KPIs
    latest_rate = df_dr['energy_rate_per_kwh'].iloc[-1] if not df_dr.empty else 0
    latest_curtailment = df_dr['curtailment_kw'].iloc[-1] if not df_dr.empty else 0
    with kpi_cols[5]: st.metric(label="💲 Grid Rate (¢/kWh)", value=f"{latest_rate * 100:.1f}")
    with kpi_cols[6]: st.metric(label="✂️ Curtailment (kW)", value=f"{latest_curtailment:.2f}", delta=f"{latest_curtailment:.2f} Req." if latest_curtailment > 0 else "None", delta_color="inverse" if latest_curtailment > 0 else "off")
    # Blockchain Wallet KPIs
    latest_balance_eth = 0.0; agent_address_display = "Fetching..."
    if not df_blockchain.empty: # Simplified fetching
        latest_entry = df_blockchain.sort_values(by='timestamp', ascending=False).iloc[0]
        if pd.notna(latest_entry['balance_eth']): latest_balance_eth = latest_entry['balance_eth']
        if pd.notna(latest_entry['agent_account']): agent_address_display = latest_entry['agent_account']
    with kpi_cols[7]: st.metric(label="💰 Wallet Balance (ETH)", value=f"{latest_balance_eth:.6f}")
    with kpi_cols[8]: st.markdown("**Negotiation Wallet**"); st.text_area("Address", value=agent_address_display, disabled=True, label_visibility="collapsed")

    # --- Chart Sections --- (Keep all chart sections as they were)
    # ... (Actual Energy Charts) ...
    # ... (Local Forecast Charts) ...
    # ... (DR & Grid Charts) ...
    # ... (Blockchain Charts/Table) ...
    st.markdown("---")
    st.header("⚡ Actual Energy Flow (From GUIAgent)")
    chart_cols_actual = st.columns(2)
    with chart_cols_actual[0]:
        st.subheader("☀️ Actual Production")
        if not df_prod.empty: st.line_chart(df_prod[['value']].rename(columns={'value': 'Prod (kW)'}), use_container_width=True)
        else: st.warning("No recent actual production data.")
    with chart_cols_actual[1]:
        st.subheader("🏠 Actual Consumption")
        if not df_cons.empty: st.line_chart(df_cons[['value']].rename(columns={'value': 'Cons (kW)'}), use_container_width=True)
        else: st.warning("No recent actual consumption data.")

    st.markdown("---")
    st.header("🔮 Energy Forecasts (Local)")
    chart_cols_pred = st.columns(2)
    with chart_cols_pred[0]:
        st.subheader("📈 Predicted Production")
        if not df_preds.empty: st.line_chart(df_preds[['predicted_production']].rename(columns={'predicted_production': 'Pred Prod (kW)'}), use_container_width=True)
        else: st.warning("No recent production forecast data.")
    with chart_cols_pred[1]:
        st.subheader("📉 Predicted Demand")
        if not df_preds.empty: st.line_chart(df_preds[['predicted_demand']].rename(columns={'predicted_demand': 'Pred Demand (kW)'}), use_container_width=True)
        else: st.warning("No recent demand forecast data.")

    st.markdown("---")
    st.header("🚦 Demand Response & Grid Signals")
    chart_cols_dr = st.columns(3)
    with chart_cols_dr[0]:
        st.subheader("💲 Energy Rate Trend")
        if not df_dr.empty:
            df_dr_rate_cents = (df_dr[['energy_rate_per_kwh']] * 100).rename(columns={'energy_rate_per_kwh': 'Rate (¢/kWh)'})
            st.line_chart(df_dr_rate_cents, use_container_width=True)
        else: st.warning("No recent energy rate data.")
    with chart_cols_dr[1]:
        st.subheader("✂️ Curtailment Trend")
        if not df_dr.empty:
             st.line_chart(df_dr[['curtailment_kw']].rename(columns={'curtailment_kw': 'Curtailment (kW)'}), use_container_width=True)
        else: st.warning("No recent curtailment data.")
    with chart_cols_dr[2]:
         st.subheader("🌐 Grid Forecast (Demand vs Supply)")
         if not df_dr.empty:
              df_grid_preds = df_dr[['grid_predicted_demand', 'grid_predicted_supply']].rename(columns={'grid_predicted_demand': 'Grid Demand (Pred)','grid_predicted_supply': 'Grid Supply (Pred)'})
              st.line_chart(df_grid_preds, use_container_width=True)
         else: st.warning("No recent grid forecast data.")

    st.markdown("---")
    st.header("🔗 Blockchain Auction Activity")
    if not df_blockchain.empty:
         st.subheader("💰 Wallet Balance Trend (ETH)")
         balance_chart_df = df_blockchain.dropna(subset=['balance_eth', 'datetime'])
         if not balance_chart_df.empty:
              balance_chart_df = balance_chart_df.set_index('datetime')[['balance_eth']]
              st.line_chart(balance_chart_df, use_container_width=True)

         st.subheader("📜 Recent Blockchain Log")
         display_cols = {'datetime': 'Timestamp', 'event_type': 'Event', 'energy_kwh': 'Energy (kWh)','price_eth': 'Price (ETH)', 'balance_eth': 'New Balance (ETH)','counterparty_address': 'Counterparty', 'status': 'Status', 'agent_account': 'Agent Acc'}
         blockchain_display_df = df_blockchain[list(display_cols.keys())].copy()
         blockchain_display_df.rename(columns=display_cols, inplace=True)
         st.dataframe(blockchain_display_df.sort_values(by='Timestamp', ascending=False),use_container_width=True, hide_index=True,
             column_config={ "Timestamp": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm:ss"), # Add others
                           })
    else: st.info("No recent blockchain activity logged.")


    # --- Raw Data Explorer --- (Ensure trade_summary is added)
    with st.expander("Raw Data Explorer"):
        st.subheader("Actual Production Data (GUIAgent)")
        st.dataframe(df_prod.sort_index(ascending=False), use_container_width=True)
        st.subheader("Actual Consumption Data (GUIAgent)")
        st.dataframe(df_cons.sort_index(ascending=False), use_container_width=True)
        st.subheader("Local Predictions Data")
        st.dataframe(df_preds.sort_index(ascending=False), use_container_width=True)
        st.subheader("Demand Response Log Data")
        st.dataframe(df_dr.sort_index(ascending=False), use_container_width=True)
        st.subheader("Trade Summary Log")
        df_summary_full = fetch_recent_data(conn, "trade_summary", history_minutes, 'timestamp')
        st.dataframe(df_summary_full.sort_values(by='timestamp', ascending=False), use_container_width=True)
        st.subheader("Blockchain Log Data")
        st.dataframe(df_blockchain.sort_values(by='timestamp', ascending=False), use_container_width=True)

    # --- Auto-refresh ---
    time.sleep(REFRESH_INTERVAL_SECONDS)
    st.rerun()

else:
    st.error("Dashboard cannot load data: Database connection failed.")