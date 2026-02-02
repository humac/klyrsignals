import streamlit as st
import pandas as pd
from utils import fetch_assets, get_auditor_data

st.set_page_config(page_title="KlyrSignals", layout="wide")

st.title("KlyrSignals Dashboard")

# Fetch Data
assets = fetch_assets()
look_through = get_auditor_data("look-through")

# Calculate Total
total_cents = 0
if look_through:
    total_cents = look_through.get("total_value_cents", 0)

total_assets_count = len(assets)

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Net Worth", f"${total_cents / 100:,.2f}")
col2.metric("Total Assets", total_assets_count)
col3.metric("Status", "Active")

st.markdown("---")

st.subheader("Your Assets")
if assets:
    df = pd.DataFrame(assets)
    # Flatten attributes for display
    # df['valuation'] = df['attributes'].apply(lambda x: x.get('valuation_cents', 0) / 100 if x else 0)
    st.dataframe(df)
else:
    st.info("No assets found. Go to 'Assets' page to add some.")
