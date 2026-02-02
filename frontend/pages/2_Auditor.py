import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import get_auditor_data

st.title("Investment Auditor")

# 1. Alerts
st.subheader("Concentration Alerts")
alerts_data = get_auditor_data("alerts")
if alerts_data and "alerts" in alerts_data:
    if not alerts_data["alerts"]:
        st.success("No concentration risks detected.")
    else:
        for alert in alerts_data["alerts"]:
            st.warning(alert)
else:
    st.info("No analysis data available.")

st.markdown("---")

# 2. Look-Through Charts
look_through = get_auditor_data("look-through")
if look_through and "exposure" in look_through:
    exposure = look_through["exposure"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Sector Allocation")
        sectors = exposure.get("sectors", {})
        if sectors:
           # Prepare data for Sunburst (Simplified as Pie for now, Sunburst requires hierarchy)
           # Task asked for Sunburst: Inner ring=Asset Class, Outer=Sector.
           # Our API currently returns flat sectors. 
           # Ideally we'd group by Asset Class -> Sector. For now, simple Pie.
           df_sec = pd.DataFrame(list(sectors.items()), columns=["Sector", "ValueCents"])
           df_sec['Value'] = df_sec['ValueCents'] / 100
           fig = px.pie(df_sec, values='Value', names='Sector', title="Sector Exposure")
           st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Sector data")

    with col2:
        st.markdown("### Geographic Exposure")
        geo = exposure.get("geography", {})
        if geo:
            # Treemap
            df_geo = pd.DataFrame(list(geo.items()), columns=["Region", "ValueCents"])
            df_geo['Value'] = df_geo['ValueCents'] / 100
            fig = px.treemap(df_geo, path=['Region'], values='Value', title="Geographic Treemap")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Geographic data")

st.markdown("---")

# 3. Correlation Matrix
st.subheader("Risk Overlap Heatmap")
corr_data = get_auditor_data("correlation_matrix")
if corr_data:
    df_corr = pd.DataFrame(corr_data)
    fig_corr = px.imshow(df_corr, text_auto=True, aspect="auto", title="36-Month Correlation Matrix")
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.info("Insufficient data for correlation matrix")
