<p align="center">
  <img src="assets/logo.png" alt="OrbitIQ Logo" width="100" height="100"/>
</p>

# OrbitIQ 🛸

> **AI-Powered Spacecraft Anomaly Detection & Mission Risk Intelligence**
>
> Transforming raw NASA telemetry from data-heavy to insight-driven — built for the IBM AI Builders Challenge: Advance Space Exploration with AI.

---

## Problem Statement

Space missions generate terabytes of telemetry, sensor readings, and environmental data every day. Yet anomaly detection is still largely manual or relies on brittle threshold-based rules. A single missed signal can end a mission — or worse. Engineers spend hours sifting through dashboards instead of acting on what matters.

**OrbitIQ** addresses this directly: given real NASA satellite telemetry data, it detects anomalies automatically using machine learning, and then explains what's wrong — and why — in plain English using IBM Granite.

---

## Solution Description

OrbitIQ is an interactive mission health dashboard that:

1. **Ingests real NASA data** — solar wind, magnetic field, and particle flux readings from NASA's DSCOVR satellite and the POWER API.
2. **Detects anomalies** — using an Isolation Forest model trained on historical telemetry to flag unusual patterns in real time.
3. **Explains findings in plain English** — IBM Granite (via watsonx) generates human-readable summaries of each anomaly and its potential mission impact.
4. **Answers natural language questions** — operators can ask "What is the current risk level for the communication system?" and receive a grounded, data-backed answer.
5. **Visualises mission risk trends** — interactive charts show anomaly scores, system health over time, and detected event windows.

---

## AI Approach & Architecture

```
NASA APIs (DSCOVR / POWER)
        │
        ▼
  data_loader.py          ← Fetches & normalises raw telemetry
        │
        ▼
  anomaly_detector.py     ← Isolation Forest anomaly scoring
        │             ↘
        │          granite_client.py  ← IBM Granite NL explanations
        │             ↗
        ▼
  Streamlit Dashboard     ← Real-time charts, alerts, Q&A interface
```

**Models & Technologies used:**

| Component | Technology |
| --- | --- |
| Anomaly Detection | scikit-learn `IsolationForest` |
| NL Explanation & Q&A | IBM Granite via watsonx.ai |
| Dashboard | Streamlit + Plotly |
| Data Source | NASA DSCOVR API, NASA POWER API |
| Language | Python 3.11+ |
| Primary Dev Tool | IBM Bob |

---

## Selected Challenge Theme

**Advance Space Exploration with AI** — August 2026 IBM AI Builders Challenge.

OrbitIQ directly addresses the challenge theme by:

- Transforming raw mission telemetry into **actionable, insight-driven alerts**
- Improving **mission safety and reliability** through early anomaly detection
- Making **complex space data accessible** to both engineers and the general public via natural language

---

## How IBM Bob Was Used

IBM Bob was the **primary development tool** throughout this project. Specifically:

- **Architecture design** — Bob helped plan the system layout, data pipeline, and AI component integration from the initial idea.
- **Code generation** — All major modules (`data_loader.py`, `anomaly_detector.py`, `granite_client.py`, and the Streamlit pages) were scaffolded and iterated with Bob.
- **Debugging** — Bob identified and resolved issues in the NASA API response parsing and model feature engineering steps.
- **Documentation** — This README, inline docstrings, and the data source guide were all drafted with Bob's assistance.
- **Challenge strategy** — Bob analysed the judging criteria and recommended the OrbitIQ concept as the highest-impact approach.

---

## Tech Stack

```
Frontend:    Streamlit
AI/LLM:      IBM Granite (watsonx.ai)
ML:          scikit-learn (IsolationForest)
Charting:    Plotly
Data:        NASA DSCOVR API, NASA POWER API
Language:    Python 3.11+
Dev Tool:    IBM Bob
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/fsamura01/orbitiq.git
cd orbitiq
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your watsonx API key and project ID
```

### 5. Run the dashboard

```bash
streamlit run app/streamlit_app.py
```

---

## Data Sources

See [`data/README.md`](data/README.md) for full details on the NASA datasets used and how to fetch them.

- **NASA DSCOVR** — Real-time solar wind, magnetic field, and plasma data from the Deep Space Climate Observatory.
- **NASA POWER API** — Meteorological and solar energy data derived from NASA satellite observations.

Both APIs are **free and require no authentication** for standard access.

---

## Project Structure

```
orbitiq/
├── app/
│   ├── streamlit_app.py          # Main dashboard entry point
│   ├── pages/
│   │   ├── 01_Mission_Overview.py
│   │   ├── 02_Anomaly_Alerts.py
│   │   └── 03_NL_Query.py
│   └── components/
│       └── charts.py
├── data/
│   └── README.md                 # Data sources & download instructions
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_anomaly_detection.ipynb
│   └── 03_model_evaluation.ipynb
├── orbitiq/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── anomaly_detector.py
│   └── granite_client.py
├── tests/
│   └── test_anomaly_detector.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Demo

[ObitIQ](https://youtu.be/T2VVwf6kefY)

## License

[MIT](LICENSE)

---

*Built with [IBM Bob](https://www.ibm.com/products/bob) as part of the IBM AI Builders Challenge — August 2026.*
