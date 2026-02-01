"""KlyrSignals Streamlit Dashboard.

Provides:
1. Portfolio overview with account breakdown
2. Geographic Treemap (size=value, color=region)
3. Sector Sunburst (Total -> Asset Class -> Sector)
4. Risk Heatmap (correlation matrix)
5. KlyrSignals alerts and AI insights
"""

import os

import streamlit as st
import requests

API_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="KlyrSignals",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    st.title("KlyrSignals")
    st.markdown("**Net Worth & Investment Blind-Spot Analysis**")

    # Sidebar: User management
    with st.sidebar:
        st.header("Configuration")

        # User selection / creation
        user_id = st.text_input("User ID (UUID)", help="Enter your user UUID")

        st.divider()

        if user_id:
            if st.button("Sync Wealthsimple Data"):
                with st.spinner("Syncing accounts and positions from SnapTrade..."):
                    try:
                        resp = requests.post(f"{API_URL}/api/v1/connections/{user_id}/sync")
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success(
                                f"Synced {data['accounts_synced']} accounts, "
                                f"{data['positions_synced']} positions"
                            )
                        else:
                            st.error(f"Sync failed: {resp.text}")
                    except requests.ConnectionError:
                        st.error("Cannot connect to API. Is the backend running?")

            if st.button("Run Full Analysis"):
                with st.spinner("Running KlyrSignals analysis pipeline..."):
                    try:
                        resp = requests.post(
                            f"{API_URL}/api/v1/analysis/{user_id}/run",
                            params={"skip_enrichment": False},
                        )
                        if resp.status_code == 200:
                            st.session_state["analysis"] = resp.json()
                            st.success("Analysis complete!")
                        else:
                            st.error(f"Analysis failed: {resp.text}")
                    except requests.ConnectionError:
                        st.error("Cannot connect to API. Is the backend running?")

            if st.button("Run Analysis (Skip Enrichment)"):
                with st.spinner("Running analysis with cached data..."):
                    try:
                        resp = requests.post(
                            f"{API_URL}/api/v1/analysis/{user_id}/run",
                            params={"skip_enrichment": True},
                        )
                        if resp.status_code == 200:
                            st.session_state["analysis"] = resp.json()
                            st.success("Analysis complete!")
                        else:
                            st.error(f"Analysis failed: {resp.text}")
                    except requests.ConnectionError:
                        st.error("Cannot connect to API.")

        st.divider()
        st.markdown("**New User?**")
        new_email = st.text_input("Email", key="new_email")
        if st.button("Create User"):
            try:
                resp = requests.post(
                    f"{API_URL}/api/v1/users/",
                    json={"email": new_email},
                )
                if resp.status_code == 201:
                    new_user = resp.json()
                    st.success(f"Created! Your User ID: `{new_user['id']}`")
                else:
                    st.error(f"Failed: {resp.text}")
            except requests.ConnectionError:
                st.error("Cannot connect to API.")

    # Main content area
    if not user_id:
        st.info("Enter your User ID in the sidebar to get started, or create a new user.")
        _show_demo_dashboard()
        return

    # Load portfolio data
    portfolio = _fetch_portfolio(user_id)
    analysis = st.session_state.get("analysis")

    if portfolio:
        _show_portfolio_overview(portfolio)

    if analysis:
        _show_analysis_results(analysis)
    elif portfolio:
        st.info("Click 'Run Full Analysis' in the sidebar to generate KlyrSignals insights.")


def _fetch_portfolio(user_id: str) -> dict | None:
    """Fetch portfolio data from the API."""
    try:
        resp = requests.get(f"{API_URL}/api/v1/positions/{user_id}")
        if resp.status_code == 200:
            return resp.json()
    except requests.ConnectionError:
        st.warning("Cannot connect to the API backend.")
    return None


def _show_portfolio_overview(portfolio: dict) -> None:
    """Display portfolio summary and holdings table."""
    st.header("Portfolio Overview")

    total_mv = portfolio["total_market_value_cents"] / 100
    total_cb = portfolio["total_cost_basis_cents"] / 100
    total_gl = portfolio["total_gain_loss_cents"] / 100
    total_gl_pct = portfolio["total_gain_loss_pct"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Market Value", f"${total_mv:,.2f}")
    col2.metric("Total Cost Basis", f"${total_cb:,.2f}")
    col3.metric("Total Gain/Loss", f"${total_gl:,.2f}", f"{total_gl_pct:+.1f}%")
    col4.metric("Accounts", len(portfolio["accounts"]))

    for acct in portfolio["accounts"]:
        with st.expander(f"{acct['account_name']} ({acct['account_type'] or 'N/A'}) - {acct['currency']}"):
            acct_mv = acct["total_market_value_cents"] / 100
            acct_gl = acct["gain_loss_cents"] / 100
            st.metric("Market Value", f"${acct_mv:,.2f}", f"{acct['gain_loss_pct']:+.1f}%")

            if acct["positions"]:
                import pandas as pd
                positions_data = []
                for p in acct["positions"]:
                    positions_data.append({
                        "Symbol": p["symbol"],
                        "Description": p.get("description", ""),
                        "Units": p["units"],
                        "Market Value": f"${p['market_value_cents'] / 100:,.2f}",
                        "Cost Basis": f"${p['cost_basis_cents'] / 100:,.2f}",
                        "Last Price": f"${p['last_price_cents'] / 100:,.2f}",
                        "Currency": p["currency"],
                    })
                st.dataframe(pd.DataFrame(positions_data), use_container_width=True)


def _show_analysis_results(analysis: dict) -> None:
    """Display full analysis results with visualizations."""
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

    st.divider()
    st.header("KlyrSignals Analysis")

    # --- Signals / Alerts ---
    signals = analysis.get("signals", [])
    if signals:
        st.subheader("Strategic Signals")
        for signal in signals:
            severity = signal.get("severity", "info")
            if severity == "critical":
                icon = "🔴"
            elif severity == "warning":
                icon = "🟡"
            else:
                icon = "🟢"

            with st.expander(f"{icon} {signal['title']}", expanded=(severity == "critical")):
                st.write(signal["description"])
                if signal.get("affected_holdings"):
                    st.write(f"**Affected:** {', '.join(signal['affected_holdings'])}")
                st.info(f"**Recommendation:** {signal['recommendation']}")

    # --- AI Summary ---
    ai_summary = analysis.get("ai_summary", "")
    if ai_summary and not ai_summary.startswith("No positions"):
        st.subheader("AI Analysis Summary")
        st.text_area("", ai_summary, height=200, disabled=True)

    # Three-column layout for visualizations
    concentration = analysis.get("concentration", {})
    correlation = analysis.get("correlation", {})

    tab1, tab2, tab3 = st.tabs(["Geographic Treemap", "Sector Sunburst", "Risk Heatmap"])

    # --- Tab 1: Geographic Treemap ---
    with tab1:
        st.subheader("Geographic Exposure")
        country_weights = concentration.get("country_weights", {})
        if country_weights:
            countries = list(country_weights.keys())
            values = list(country_weights.values())

            fig = px.treemap(
                names=countries,
                parents=["Portfolio"] * len(countries),
                values=values,
                title="Geographic Allocation (Look-Through)",
                color=values,
                color_continuous_scale="RdYlGn_r",
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            # Home bias indicator
            home_bias = concentration.get("home_bias_pct", 0)
            st.metric(
                "Canadian Home Bias",
                f"{home_bias:.1f}%",
                delta=f"{home_bias - 60:.1f}% vs 60% threshold"
                if home_bias > 0 else None,
                delta_color="inverse",
            )
        else:
            st.info("No geographic data available. Run enrichment first.")

    # --- Tab 2: Sector Sunburst ---
    with tab2:
        st.subheader("Sector Exposure (Look-Through)")
        sector_weights = concentration.get("sector_weights", {})
        if sector_weights:
            # Build sunburst data
            labels = ["Portfolio"]
            parents = [""]
            values_sb = [0]

            # Group into asset classes
            equity_sectors = []
            fi_sectors = []
            for sector, pct in sector_weights.items():
                if sector == "Fixed Income":
                    fi_sectors.append((sector, pct))
                else:
                    equity_sectors.append((sector, pct))

            if equity_sectors:
                labels.append("Equity")
                parents.append("Portfolio")
                equity_total = sum(p for _, p in equity_sectors)
                values_sb.append(equity_total)

                for sector, pct in sorted(equity_sectors, key=lambda x: -x[1]):
                    labels.append(sector)
                    parents.append("Equity")
                    values_sb.append(pct)

            if fi_sectors:
                labels.append("Fixed Income")
                parents.append("Portfolio")
                fi_total = sum(p for _, p in fi_sectors)
                values_sb.append(fi_total)

                for sector, pct in fi_sectors:
                    labels.append(f"{sector} ")  # Append space to avoid duplicate label
                    parents.append("Fixed Income")
                    values_sb.append(pct)

            fig = px.sunburst(
                names=labels,
                parents=parents,
                values=values_sb,
                title="Asset Class -> Sector Breakdown",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

            # Concentration alerts
            alerts = concentration.get("alerts", [])
            if alerts:
                st.subheader("Concentration Alerts")
                for alert in alerts:
                    severity_color = "🔴" if alert["severity"] == "critical" else "🟡"
                    st.write(
                        f"{severity_color} **{alert['category'].title()}**: "
                        f"{alert['name']} at {alert['weight_pct']:.1f}% "
                        f"(threshold: {alert['threshold_pct']:.0f}%)"
                    )
        else:
            st.info("No sector data available. Run enrichment first.")

    # --- Tab 3: Risk Heatmap ---
    with tab3:
        st.subheader("Correlation Matrix (Risk Heatmap)")
        corr_matrix = correlation.get("correlation_matrix", {})
        if corr_matrix and len(corr_matrix) >= 2:
            symbols = list(corr_matrix.keys())
            matrix_data = []
            for sym in symbols:
                row = [corr_matrix[sym].get(s, 0) for s in symbols]
                matrix_data.append(row)

            fig = go.Figure(data=go.Heatmap(
                z=matrix_data,
                x=symbols,
                y=symbols,
                colorscale="RdBu_r",
                zmin=-1,
                zmax=1,
                text=[[f"{v:.2f}" for v in row] for row in matrix_data],
                texttemplate="%{text}",
                textfont={"size": 10},
            ))
            fig.update_layout(
                title="Pairwise Correlation Matrix (36-Month Returns)",
                height=500,
                xaxis_tickangle=-45,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Hidden twins
            twins = correlation.get("hidden_twins", [])
            if twins:
                st.subheader("Hidden Twins Detected")
                for twin in twins:
                    st.warning(
                        f"**{twin['symbol_a']}** & **{twin['symbol_b']}** "
                        f"(r = {twin['correlation']:.2f})\n\n"
                        f"{twin['explanation']}"
                    )
        else:
            st.info(
                "Need at least 2 holdings with price history for correlation analysis. "
                "Run full analysis with enrichment enabled."
            )


def _show_demo_dashboard() -> None:
    """Show a demo dashboard with sample data when no user is connected."""
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

    st.divider()
    st.subheader("Demo: What KlyrSignals Can Show You")

    # Sample data
    demo_sectors = {
        "Financials": 28.5, "Technology": 18.2, "Industrials": 12.1,
        "Healthcare": 10.5, "Energy": 8.2, "Fixed Income": 15.0,
        "Consumer Discretionary": 7.5,
    }

    demo_countries = {
        "CAN": 45.0, "USA": 38.0, "JPN": 5.5,
        "GBR": 4.2, "DEU": 3.8, "OTHER": 3.5,
    }

    col1, col2 = st.columns(2)

    with col1:
        fig = px.treemap(
            names=list(demo_countries.keys()),
            parents=["Portfolio"] * len(demo_countries),
            values=list(demo_countries.values()),
            title="Sample Geographic Treemap",
            color=list(demo_countries.values()),
            color_continuous_scale="RdYlGn_r",
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        labels = ["Portfolio"]
        parents = [""]
        values = [0]
        for sector, pct in demo_sectors.items():
            labels.append(sector)
            parents.append("Portfolio")
            values.append(pct)

        fig = px.sunburst(
            names=labels, parents=parents, values=values,
            title="Sample Sector Sunburst",
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Sample correlation heatmap
    demo_symbols = ["VGRO.TO", "XIC.TO", "BNS.TO", "TD.TO", "VFV.TO"]
    demo_corr = [
        [1.00, 0.85, 0.72, 0.74, 0.88],
        [0.85, 1.00, 0.82, 0.84, 0.65],
        [0.72, 0.82, 1.00, 0.93, 0.55],
        [0.74, 0.84, 0.93, 1.00, 0.58],
        [0.88, 0.65, 0.55, 0.58, 1.00],
    ]

    fig = go.Figure(data=go.Heatmap(
        z=demo_corr, x=demo_symbols, y=demo_symbols,
        colorscale="RdBu_r", zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in demo_corr],
        texttemplate="%{text}",
    ))
    fig.update_layout(title="Sample Correlation Heatmap", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "This is sample data. Connect your Wealthsimple account via SnapTrade "
        "to see your real portfolio analysis."
    )


if __name__ == "__main__":
    main()
