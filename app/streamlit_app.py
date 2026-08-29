"""
streamlit_app.py -- OrbitIQ main Streamlit dashboard entry point.

Run with:
    streamlit run app/streamlit_app.py
"""

import logging
import sys
from pathlib import Path

import streamlit as st

# Make the orbitiq package importable when running from the repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="OrbitIQ",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🛸 OrbitIQ")
    st.caption("AI-Powered Spacecraft Anomaly Detection")
    st.divider()
    st.markdown(
        """
        **Navigation**
        - Home (this page)
        - Mission Overview
        - Anomaly Alerts
        - Ask OrbitIQ (NL Q&A)
        """
    )
    st.divider()
    st.caption("Built with IBM Bob · IBM Granite · NASA Open Data")

# ---------------------------------------------------------------------------
# Home page content
# ---------------------------------------------------------------------------
st.title("OrbitIQ 🛸")
st.subheader("AI-Powered Spacecraft Anomaly Detection & Mission Risk Intelligence")

st.markdown(
    """
    OrbitIQ ingests real-time NASA satellite telemetry, detects anomalies using
    machine learning, and explains findings in plain English using **IBM Granite**.

    Use the **sidebar pages** to explore the dashboard:

    | Page | What you will find |
    |---|---|
    | **Mission Overview** | Live solar wind trends & system health summary |
    | **Anomaly Alerts** | ML-detected anomalies with risk scores |
    | **Ask OrbitIQ** | Natural language Q&A about mission status |
    """
)

st.divider()

# ---------------------------------------------------------------------------
# Quick-status strip
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Data Source", value="NASA DSCOVR", delta="Live")

with col2:
    st.metric(label="Model", value="Isolation Forest", delta="Ready")

with col3:
    st.metric(label="AI Engine", value="IBM Granite", delta="watsonx")

with col4:
    st.metric(label="Status", value="Online", delta="All systems nominal")

st.divider()

st.info(
    "Navigate to **Mission Overview** in the sidebar to load live NASA data and begin analysis.",
    icon="🚀",
)
