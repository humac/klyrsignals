import streamlit as st
from utils import create_manual_asset

st.title("Asset Management")

st.subheader("Add Manual Asset")
col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Asset Name", placeholder="e.g. 6-Plex Rental")
    asset_type = st.selectbox("Type", ["FIXED", "BUSINESS", "LIQUID", "CRYPTO", "LIABILITY"])

with col2:
    val_val = st.number_input("Valuation ($)", min_value=0.0, step=100.0)
    proxy = st.text_input("Proxy Ticker (Optional)", placeholder="e.g. XRE.TO")

if st.button("Create Asset"):
    val_cents = int(val_val * 100)
    if create_manual_asset(name, asset_type, val_cents, proxy if proxy else None):
        st.success(f"Created {name}")
    else:
        st.error("Failed to create asset")
