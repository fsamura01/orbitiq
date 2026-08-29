"""
02_Anomaly_Alerts.py -- ML-detected anomalies with risk scores and AI explanations.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orbitiq.anomaly_detector import AnomalyDetector
from orbitiq.data_loader import fetch_dscovr_combined

st.set_page_config(page_title="Anomaly Alerts | OrbitIQ", page_icon="⚠️", layout="wide")

st.title("Anomaly Alerts")
st.caption("Isolation Forest anomaly detection on live DSCOVR telemetry")

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
with st.sidebar:
    threshold = st.slider("Anomaly score threshold", min_value=0.5, max_value=0.99, value=0.70, step=0.01)
    contamination = st.slider("Expected anomaly rate", min_value=0.01, max_value=0.20, value=0.05, step=0.01)
    st.caption("Adjust sensitivity to tune the number of detected events.")

# ---------------------------------------------------------------------------
# Load & score
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_and_score(contamination: float, threshold: float) -> pd.DataFrame:
    df = fetch_dscovr_combined()
    detector = AnomalyDetector(contamination=contamination)
    return detector.fit_predict(df, threshold=threshold)


with st.spinner("Running anomaly detection ..."):
    try:
        df = load_and_score(contamination, threshold)
    except Exception as exc:
        st.error(f"Detection failed: {exc}")
        st.stop()

anomalies = df[df["is_anomaly"]]

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", f"{len(df):,}")
col2.metric("Anomalies Detected", f"{len(anomalies):,}", delta=f"{len(anomalies)/len(df)*100:.1f}% of data")
col3.metric("Max Anomaly Score", f"{df['anomaly_score'].max():.3f}")

st.divider()

# ---------------------------------------------------------------------------
# Anomaly score chart
# ---------------------------------------------------------------------------
from app.components.charts import anomaly_score_chart

st.subheader("Anomaly Score Over Time")
st.plotly_chart(anomaly_score_chart(df, threshold=threshold), use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Anomaly table with AI explanations
# ---------------------------------------------------------------------------
st.subheader(f"Detected Anomalies ({len(anomalies)} events)")

if anomalies.empty:
    st.success("No anomalies detected at the current threshold. Try lowering the slider.")
else:
    display_cols = [c for c in ["time_tag", "speed", "density", "temperature", "bt", "bz_gsm", "anomaly_score"] if c in anomalies.columns]
    st.dataframe(
        anomalies[display_cols].sort_values("anomaly_score", ascending=False).reset_index(drop=True),
        use_container_width=True,
    )

    st.divider()
    st.subheader("AI Explanation (IBM Granite)")
    st.caption("Select an anomaly event to get a plain-English explanation from IBM Granite.")

    top_anomaly = anomalies.sort_values("anomaly_score", ascending=False).iloc[0]
    stats = top_anomaly.to_dict()
    stats["timestamp"] = str(stats.get("time_tag", ""))

    if st.button("Explain top anomaly with IBM Granite"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            from orbitiq.granite_client import GraniteClient, RateLimitError
            with st.spinner("Asking IBM Granite ..."):
                client = GraniteClient()
                explanation = client.explain_anomaly(stats)
            st.info(explanation, icon="🤖")
        except EnvironmentError as exc:
            st.warning(f"watsonx credentials not configured: {exc}", icon="⚠️")
        except RateLimitError:
            st.warning(
                "**Rate limit reached** — the free watsonx plan allows only 10 concurrent "
                "requests. Wait a few seconds and click the button again.",
                icon="⏳",
            )
        except Exception as exc:
            st.error(f"IBM Granite error: {exc}")
