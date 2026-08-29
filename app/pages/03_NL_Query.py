"""
03_NL_Query.py -- Ask OrbitIQ: natural language Q&A about mission health.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Ask OrbitIQ | NL Query", page_icon="💬", layout="wide")

st.title("Ask OrbitIQ")
st.caption("Natural language Q&A about current mission health — powered by IBM Granite")

st.markdown(
    """
    Ask any question about the spacecraft telemetry and OrbitIQ will answer it
    using live NASA data as context. **Examples:**

    - *What is the current risk level for spacecraft communication systems?*
    - *Is there any geomagnetic storm risk in the next few hours?*
    - *What does the current solar wind speed mean for mission safety?*
    - *Summarise the anomalies detected today.*
    """
)

st.divider()

# ---------------------------------------------------------------------------
# Build telemetry context string from live data
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def build_telemetry_context() -> str:
    from orbitiq.data_loader import fetch_dscovr_combined

    try:
        df = fetch_dscovr_combined()
        latest = df.iloc[-1]
        recent_anomalies = _count_recent_anomalies(df)
        return (
            f"Latest DSCOVR reading ({latest.get('time_tag', 'unknown')}):\n"
            f"  Solar wind speed : {latest.get('speed', 'N/A')} km/s\n"
            f"  Proton density   : {latest.get('density', 'N/A')} n/cm3\n"
            f"  Temperature      : {latest.get('temperature', 'N/A')} K\n"
            f"  IMF Bt (total)   : {latest.get('bt', 'N/A')} nT\n"
            f"  IMF Bz           : {latest.get('bz_gsm', 'N/A')} nT\n"
            f"Recent anomaly events (last 7 days, score > 0.7): {recent_anomalies}\n"
        )
    except Exception as exc:
        return f"[Telemetry unavailable: {exc}]"


def _count_recent_anomalies(df) -> int:
    try:
        from orbitiq.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector()
        result = detector.fit_predict(df)
        return int(result["is_anomaly"].sum())
    except Exception:
        return -1


# ---------------------------------------------------------------------------
# Q&A interface
# ---------------------------------------------------------------------------
context = build_telemetry_context()

with st.expander("View current telemetry context sent to IBM Granite"):
    st.code(context, language="text")

question = st.text_input(
    "Your question:",
    placeholder="What is the current risk level for spacecraft communication systems?",
    key="nl_question",
)

if st.button("Ask OrbitIQ", type="primary") and question.strip():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        from orbitiq.granite_client import GraniteClient, RateLimitError
        with st.spinner("IBM Granite is thinking ..."):
            client = GraniteClient()
            answer = client.answer_question(question, context)
        st.subheader("OrbitIQ Response")
        st.info(answer, icon="🛰️")
    except EnvironmentError as exc:
        st.warning(
            f"IBM Granite is not configured yet.\n\n"
            f"{exc}\n\n"
            "Copy `.env.example` to `.env` and add your watsonx credentials.",
            icon="⚠️",
        )
    except RateLimitError:
        st.warning(
            "**Rate limit reached** — the free watsonx plan allows only 10 concurrent "
            "requests. Wait a few seconds and ask again.",
            icon="⏳",
        )
    except Exception as exc:
        st.error(f"Error: {exc}")
elif st.button("Ask OrbitIQ", disabled=True, key="disabled_ask"):
    pass  # placeholder to avoid duplicate key warning when input is empty

st.divider()
st.caption("IBM Granite responses are grounded in live NASA DSCOVR telemetry. Always verify critical decisions with mission engineers.")
