import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TradePad", layout="wide")

st.title("🦅 TradePad - Shared Cloud Journal")
st.write("Log your setups, track your equity, and save your data forever.")

# --- USER LOGIN SECTION ---
st.sidebar.header("👤 Trader Authentication")
username = st.sidebar.text_input("Enter your Username:", "").strip().lower()

if not username:
    st.warning("Please enter a username in the sidebar to view or log your trades.")
else:
    st.sidebar.success(type=f"Logged in as: {username}")

    # --- CONNECT TO DATABASE ---
    # We use Streamlit's built-in cloud database connection
    db = st.connection("firestore", type="firestore")

    # Define where this user's trades are stored in the cloud
    user_ref = db.collection("traders").document(username)

    # Fetch existing trades for this user from the cloud database
    user_doc = user_ref.get()
    if user_doc.exists:
        trades_list = user_doc.to_dict().get("trades", [])
    else:
        trades_list = []

    # --- NEW TRADE INPUT FORM ---
    st.subheader("📝 Log a New Setup")

    with st.form("trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            asset = col1.selectbox("Asset Pair", ["USTEC (Nasdaq)", "US30 (Dow Jones)", "DE30 (DAX)", "XAUUSD (Gold)"])
            direction = col1.selectbox("Direction", ["BUY", "SELL"])
        with col2:
            pips = col2.number_input("Pips Gained/Lost (+/-)", value=0.0, step=0.1)
            pnl = col2.number_input("Profit/Loss ($)", value=0.0, step=1.0)
        with col3:
            session = col3.selectbox("Session", ["London Open", "NY PM Session", "Asians / Rest"])
            notes = col3.text_input("Trade Notes / Setup Type", placeholder="e.g., Fair Value Gap / Liquidity Sweep")

        submit = st.form_submit_button("Save Trade to Cloud")

    # --- SAVE TO CLOUD ACTION ---
    if submit:
        new_trade = {
            "Asset": asset,
            "Direction": direction,
            "Pips": pips,
            "PnL": pnl,
            "Session": session,
            "Notes": notes
        }
        # Add new trade to local list and push entire list back to the cloud database
        trades_list.append(new_trade)
        user_ref.set({"trades": trades_list})
        st.success("Trade securely saved to the cloud! Refreshing dashboard...")
        st.rerun()

    # --- DASHBOARD LOGIC ---
    if trades_list:
        df = pd.DataFrame(trades_list)

        # Calculate Equity Curve
        df['Equity'] = df['PnL'].cumsum()

        # Display Stats Metrics
        total_trades = len(df)
        total_pnl = df['PnL'].sum()
        win_rate = (len(df[df['PnL'] > 0]) / total_trades) * 100 if total_trades > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Trades Logged", f"{total_trades}")
        m2.metric("Net Profit / Loss", f"${total_pnl:,.2f}")
        m3.metric("Win Rate", f"{win_rate:.1f}%")

        st.markdown("---")

        # Visual Chart & Table
        fig = px.line(df, y='Equity', title="🚀 Your Cloud Equity Curve", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Your Trading Ledger")
        st.dataframe(df[["Asset", "Direction", "Pips", "PnL", "Session", "Notes"]], use_container_width=True)
    else:
        st.info("No trades found in the cloud database for this username yet. Log your first setup above!")