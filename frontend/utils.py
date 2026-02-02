import requests
import os
import streamlit as st

def get_backend_url():
    # In Docker, this is 'http://backend:8000'
    # When running locally, it might be 'http://localhost:8000'
    # We use os.getenv, but fallback to localhost for local dev if not defined in env
    return os.getenv("BACKEND_URL", "http://localhost:8000")

def fetch_assets():
    url = f"{get_backend_url()}/assets/"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception as e:
        st.error(f"Error fetching assets: {e}")
        return []

def create_manual_asset(name, asset_type, valuation_cents, proxy_ticker=None):
    url = f"{get_backend_url()}/assets/"
    payload = {
        "name": name,
        "type": asset_type,
        "attributes": {
            "valuation_cents": valuation_cents,
            "proxy_ticker": proxy_ticker
        }
    }
    try:
        resp = requests.post(url, json=payload)
        return resp.status_code == 200
    except Exception as e:
        st.error(f"Error creating asset: {e}")
        return False

def get_auditor_data(endpoint):
    url = f"{get_backend_url()}/auditor/{endpoint}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
        return {}
    except Exception as e:
        st.error(f"Error fetching auditor data: {e}")
        return {}
