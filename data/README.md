# Data Sources

OrbitIQ uses two free NASA APIs. No authentication is required for standard access.

---

## 1. NASA DSCOVR — Real-Time Solar Wind Data

**What it is:** NOAA's Real-Time Solar Wind (RTSW) feed sourced from the ACE and DSCOVR satellites at the L1 Lagrange point, ~1.5 million km from Earth. Provides 1-minute cadence solar wind measurements — the primary data source for space weather anomaly detection.

**Endpoint:**
```
https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json   <- plasma (speed, density, temperature)
https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json    <- magnetic field (Bx, By, Bz, Bt)
```

> **Note:** The older `products/solar-wind/plasma-7-day.json` and `mag-7-day.json` endpoints were retired by NOAA. The RTSW endpoints above are the current live replacements (~2 days of 1-minute data, ~3000 records).

**Key fields used:**

| Field | Description |
|---|---|
| `time_tag` | UTC timestamp |
| `density` | Solar wind proton density (n/cm³) |
| `speed` | Solar wind bulk speed (km/s) |
| `temperature` | Proton temperature (K) |
| `bx`, `by`, `bz` | Interplanetary magnetic field components (nT) |
| `bt` | Total magnetic field strength (nT) |

**Anomaly signals:**
- Sudden spike in solar wind speed (> 700 km/s) → potential geomagnetic storm
- Sharp drop in density followed by speed surge → CME (Coronal Mass Ejection) arrival
- Strongly negative `bz` component → high risk of geomagnetic disturbance

**Fetch example:**
```python
import requests, pandas as pd

url = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
df = pd.DataFrame(requests.get(url).json())
df["time_tag"] = pd.to_datetime(df["time_tag"], utc=True)
df = df.rename(columns={"proton_speed": "speed", "proton_density": "density", "proton_temperature": "temperature"})
```

---

## 2. NASA POWER API — Atmospheric & Solar Energy Data

**What it is:** NASA's Prediction Of Worldwide Energy Resources (POWER) project provides meteorological and solar energy data derived from satellite observations. Useful for ground-station and launch window analysis.

**Endpoint:**
```
https://power.larc.nasa.gov/api/temporal/daily/point
  ?parameters=ALLSKY_SFC_SW_DWN,T2M,WS10M
  &community=RE
  &longitude={lon}
  &latitude={lat}
  &start={YYYYMMDD}
  &end={YYYYMMDD}
  &format=JSON
```

**Key parameters used:**

| Parameter | Description |
|---|---|
| `ALLSKY_SFC_SW_DWN` | All-sky surface shortwave downward irradiance (Wh/m²/day) |
| `T2M` | Temperature at 2 metres (°C) |
| `WS10M` | Wind speed at 10 metres (m/s) |

**Fetch example:**
```python
import requests

params = {
    "parameters": "ALLSKY_SFC_SW_DWN,T2M,WS10M",
    "community": "RE",
    "longitude": -80.6,
    "latitude": 28.5,   # Kennedy Space Center
    "start": "20240101",
    "end": "20241231",
    "format": "JSON",
}
resp = requests.get("https://power.larc.nasa.gov/api/temporal/daily/point", params=params)
data = resp.json()["properties"]["parameter"]
```

---

## Local Data Directory Layout

```
data/
├── README.md          ← this file
├── raw/               ← gitignored — raw API downloads
└── processed/         ← gitignored — cleaned, feature-engineered CSVs
```

Run `notebooks/01_data_exploration.ipynb` to fetch and cache a local copy of both datasets.
