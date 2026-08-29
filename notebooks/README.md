# Notebooks

Run these notebooks in order to reproduce the full OrbitIQ analysis pipeline.

| Notebook | Purpose |
|---|---|
| `01_data_exploration.ipynb` | Fetch NASA DSCOVR & POWER data, EDA, visualise sensor distributions |
| `02_anomaly_detection.ipynb` | Train Isolation Forest, tune contamination, plot anomaly score timeline |
| `03_model_evaluation.ipynb` | Precision/recall analysis, confusion matrix, feature importance |

## Setup

```bash
pip install -r ../requirements.txt
jupyter lab
```

Notebooks write cached data to `../data/raw/` and `../data/processed/` (both gitignored).
