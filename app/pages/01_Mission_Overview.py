"""
01_Mission_Overview.py -- Live solar wind trends & system health summary.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orbitiq.data_loader import fetch_dscovr_combined

st.set_page_config(page_title="Mission Overview | OrbitIQ", page_icon="📡", layout="wide")

st.title("Mission Overview")
st.caption("Real-time DSCOVR solar wind telemetry (last 7 days)")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)  # refresh every 5 minutes
def load_data() -> pd.DataFrame:
    return fetch_dscovr_combined()


with st.spinner("Fetching NASA DSCOVR telemetry ..."):
    try:
        df = load_data()
        st.success(f"Loaded {len(df):,} telemetry records.")
    except Exception as exc:
        st.error(f"Failed to fetch data: {exc}")
        st.stop()

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------
latest = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Solar Wind Speed", f"{latest['speed']:.0f} km/s", help="Bulk solar wind proton speed")
col2.metric("Proton Density", f"{latest['density']:.1f} n/cm³", help="Solar wind proton density")
col3.metric("Temperature", f"{latest['temperature']:.0e} K", help="Solar wind proton temperature")
col4.metric("Magnetic Field Bz", f"{latest.get('bz_gsm', float('nan')):.1f} nT", help="IMF Bz component (negative = geomagnetic storm risk)")

st.divider()

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
from app.components.charts import time_series_chart

st.subheader("Solar Wind Speed (km/s)")
st.plotly_chart(time_series_chart(df, x="time_tag", y="speed", color="#3b82d4"), use_container_width=True)

st.subheader("Proton Density (n/cm³)")
st.plotly_chart(time_series_chart(df, x="time_tag", y="density", color="#7c5cd8"), use_container_width=True)

st.subheader("IMF Bz Component (nT)")
st.plotly_chart(time_series_chart(df, x="time_tag", y="bz_gsm", color="#e05c5c", zero_line=True), use_container_width=True)

st.divider()
st.caption("Data: NASA DSCOVR via NOAA Space Weather Prediction Center. Refreshes every 5 minutes.")
