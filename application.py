import streamlit as st
import pandas as pd
import plotly.express as px

# Set up the page style and brand name
st.set_page_config(page_title="TradePad | Private Journal", layout="wide")
st.title("📝 TradePad")
st.subheader("Your Private Trading Journal & Analytics Dashboard")
st.write("Track your trading strategy and discover your statistical edge. Your data stays local to your session.")

# --- SESSION STATE: KEEP DATA PRIVATE PER USER ---
if "my_trades" not in st.session_state:
    st.session_state.my_trades = pd.DataFrame(
        columns=["Date", "Asset / Pair", "Type", "Entry Price", "Exit Price", "Result ($)", "Notes"]
    )

df = st.session_state.my_trades

# --- SIDEBAR: INPUT NEW TRADE ---
st.sidebar.header("📝 Log a New Trade")
with st.sidebar.form("trade_form", clear_on_submit=True):
    date = st.date_input("Trade Date")

    # ONE CLEAN DROPDOWN: Separated by exact Exness symbols
    asset = st.selectbox("Asset / Pair", [
        "US500 (S&P 500)",
        "USTEC (Nasdaq 100)",
        "US30 (Dow Jones)",
        "DE30 (Dax 40)",
        "XAUUSD (Gold)",
        "USOIL (Crude Oil)",
        "EURUSD",
        "GBPUSD",
        "USDJPY",
        "GBPJPY",
        "EURGBP",
        "AUDUSD",
        "USDCAD",
        "BTCUSD (Bitcoin)",
        "ETHUSD (Ethereum)"
    ])

    trade_type = st.selectbox("Type", ["BUY (Long)", "SELL (Short)"])
    entry = st.number_input("Entry Price", min_value=0.0, format="%.5f")
    exit_p = st.number_input("Exit Price", min_value=0.0, format="%.5f")
    result = st.number_input("Profit/Loss (in USD $)", format="%.2f")
    notes = st.text_area("Notes (e.g., 'Clean 15m ORB setup')")

    submit = st.form_submit_button("Save to TradePad")

if submit:
    new_trade = pd.DataFrame([[date, asset, trade_type, entry, exit_p, result, notes]], columns=df.columns)
    st.session_state.my_trades = pd.concat([df, new_trade], ignore_index=True)
    st.sidebar.success("Trade saved to your TradePad!")
    st.rerun()

# --- MAIN DASHBOARD ---
if not df.empty:
    # Calculations
    total_trades = len(df)
    win_trades = len(df[df["Result ($)"] > 0])
    win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = df["Result ($)"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trades", total_trades)
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Net Profit/Loss", f"${total_pnl:,.2f}")

    # Interactive Performance Chart
    st.subheader("📈 Equity Curve")
    df["Cumulative PnL"] = df["Result ($)"].cumsum()
    fig = px.line(df, x=df.index, y="Cumulative PnL", title="Account Growth ($)", markers=True)
    fig.update_traces(line_color="#00FFCC")  # Sleek tech green look
    st.plotly_chart(fig, use_container_width=True)

    # Display raw data table
    st.subheader("📁 History Log")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Your TradePad is empty. Use the sidebar to log your first trade for this session!")