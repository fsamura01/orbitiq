"""
anomaly_detector.py -- Isolation Forest anomaly detection for telemetry.

Usage:
    detector = AnomalyDetector()
    detector.fit(df_train)
    scores = detector.score(df_live)    # higher = more anomalous (0-1)
    flags  = detector.predict(df_live)  # True where anomaly detected
"""

from __future__ import annotations

import logging
from typing import List, Optional, Union, cast

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

DEFAULT_FEATURES: List[str] = [
    "density",
    "speed",
    "temperature",
    "bt",
    "bz_gsm",
]


class AnomalyDetector:
    """Isolation Forest wrapper for spacecraft telemetry anomaly detection.

    Scores are normalised to [0, 1] where 1 = maximally anomalous.
    """

    def __init__(
        self,
        features: Optional[List[str]] = None,
        contamination: Union[float, str] = 0.05,
        n_estimators: int = 200,
        random_state: int = 42,
    ) -> None:
        self.features = features or DEFAULT_FEATURES
        self._scaler = StandardScaler()
        self._model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,  # type: ignore[arg-type]
            random_state=random_state,
        )
        self._fitted = False

    def fit(self, df: pd.DataFrame) -> "AnomalyDetector":
        """Fit scaler and Isolation Forest on baseline telemetry."""
        X = self._extract(df)
        self._scaler.fit_transform(X)
        self._model.fit(self._scaler.transform(X))
        self._fitted = True
        logger.info("AnomalyDetector fitted on %d samples.", len(X))
        return self

    def score(self, df: pd.DataFrame) -> np.ndarray:
        """Return anomaly scores in [0, 1] for each row (higher = more anomalous)."""
        self._assert_fitted()
        X = self._scaler.transform(self._extract(df))
        raw = self._model.score_samples(X)
        scores = 1.0 - (raw - raw.min()) / (raw.max() - raw.min() + 1e-9)
        return scores

    def predict(self, df: pd.DataFrame, threshold: float = 0.7) -> pd.Series:
        """Return boolean Series flagging rows above the anomaly threshold."""
        scores = self.score(df)
        return pd.Series(scores >= threshold, index=df.index, name="is_anomaly")

    def fit_predict(self, df: pd.DataFrame, threshold: float = 0.7) -> pd.DataFrame:
        """Convenience: fit on df, then attach score and flag columns."""
        self.fit(df)
        df = df.copy()
        df["anomaly_score"] = self.score(df)
        df["is_anomaly"] = df["anomaly_score"] >= threshold
        return df

    def _extract(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = [c for c in self.features if c not in df.columns]
        if missing:
            raise ValueError(f"DataFrame missing required columns: {missing}")
        return cast(pd.DataFrame, df[self.features].dropna())

    def _assert_fitted(self) -> None:
        if not self._fitted:
            raise RuntimeError("Call fit() before score() or predict().")
