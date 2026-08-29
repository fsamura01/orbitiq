"""
data_loader.py -- Fetch and normalise NASA/NOAA telemetry data.

Two sources are supported:
  - NOAA RTSW (Real-Time Solar Wind) 1-minute plasma & magnetic field (~3000 records, ~2 days)
  - NASA POWER API (daily ground/atmospheric data for a lat/lon point)
"""

from __future__ import annotations

import logging
from datetime import date

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# NOAA Real-Time Solar Wind (RTSW) — 1-minute resolution, ~2 days rolling
# Replaced the retired products/solar-wind/plasma-7-day.json endpoints
# ---------------------------------------------------------------------------
_RTSW_WIND_URL = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
_RTSW_MAG_URL  = "https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json"

# NASA POWER API base
_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def fetch_dscovr_plasma() -> pd.DataFrame:
    """Return RTSW solar wind plasma measurements (~2 days, 1-minute cadence).

    Columns: time_tag, density, speed, temperature
    """
    logger.info("Fetching RTSW plasma data ...")
    response = requests.get(_RTSW_WIND_URL, timeout=15)
    response.raise_for_status()

    df = pd.DataFrame(response.json())
    df["time_tag"] = pd.to_datetime(df["time_tag"], utc=True)

    # Rename to the column names the rest of the app expects
    df = df.rename(columns={
        "proton_density":     "density",
        "proton_speed":       "speed",
        "proton_temperature": "temperature",
    })

    numeric_cols = ["density", "speed", "temperature"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=numeric_cols)
    df = df.sort_values("time_tag").reset_index(drop=True)
    logger.info("Fetched %d plasma records.", len(df))
    return df[["time_tag", "density", "speed", "temperature"]]


def fetch_dscovr_mag() -> pd.DataFrame:
    """Return RTSW interplanetary magnetic field measurements (~2 days, 1-minute cadence).

    Columns: time_tag, bx_gsm, by_gsm, bz_gsm, bt
    """
    logger.info("Fetching RTSW magnetic field data ...")
    response = requests.get(_RTSW_MAG_URL, timeout=15)
    response.raise_for_status()

    df = pd.DataFrame(response.json())
    df["time_tag"] = pd.to_datetime(df["time_tag"], utc=True)

    for col in ("bx_gsm", "by_gsm", "bz_gsm", "bt"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["bt"]).sort_values("time_tag").reset_index(drop=True)
    logger.info("Fetched %d magnetic field records.", len(df))
    return df[["time_tag", "bx_gsm", "by_gsm", "bz_gsm", "bt"]]


def fetch_dscovr_combined() -> pd.DataFrame:
    """Merge plasma and magnetic field streams on the nearest timestamp.

    Returns a single DataFrame with all sensor columns.
    """
    plasma = fetch_dscovr_plasma()
    mag    = fetch_dscovr_mag()

    df = pd.merge_asof(
        plasma.sort_values("time_tag"),
        mag.sort_values("time_tag"),
        on="time_tag",
        direction="nearest",
        tolerance=pd.Timedelta("2min"),
    )
    logger.info("Combined dataset: %d rows, %d columns.", *df.shape)
    return df


def fetch_nasa_power(
    lat: float,
    lon: float,
    start: date,
    end: date,
    parameters: str = "ALLSKY_SFC_SW_DWN,T2M,WS10M",
) -> pd.DataFrame:
    """Fetch daily NASA POWER data for a location and date range.

    Args:
        lat: Latitude (decimal degrees, -90 to 90).
        lon: Longitude (decimal degrees, -180 to 180).
        start: Start date (inclusive).
        end: End date (inclusive).
        parameters: Comma-separated POWER parameter codes.

    Returns:
        DataFrame indexed by date with one column per parameter.
    """
    logger.info("Fetching NASA POWER data for (%.2f, %.2f) ...", lat, lon)
    params = {
        "parameters": parameters,
        "community":  "RE",
        "longitude":  lon,
        "latitude":   lat,
        "start":      start.strftime("%Y%m%d"),
        "end":        end.strftime("%Y%m%d"),
        "format":     "JSON",
    }
    response = requests.get(_POWER_BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()["properties"]["parameter"]
    df = pd.DataFrame(payload)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "date"
    df = df.replace(-999.0, float("nan"))  # POWER uses -999 as missing value
    logger.info("Fetched %d daily POWER records.", len(df))
    return df
