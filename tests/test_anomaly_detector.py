"""
test_anomaly_detector.py -- Unit tests for AnomalyDetector.
"""

import numpy as np
import pandas as pd
import pytest

from orbitiq.anomaly_detector import AnomalyDetector, DEFAULT_FEATURES


def _make_df(n: int = 200, seed: int = 0) -> pd.DataFrame:
    """Generate a synthetic telemetry DataFrame for testing."""
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "density": rng.normal(5.0, 1.5, n),
            "speed": rng.normal(450.0, 50.0, n),
            "temperature": rng.normal(1e5, 2e4, n),
            "bt": rng.normal(5.0, 2.0, n),
            "bz_gsm": rng.normal(0.0, 3.0, n),
        }
    )


def test_fit_predict_returns_score_and_flag_columns():
    df = _make_df()
    detector = AnomalyDetector()
    result = detector.fit_predict(df)
    assert "anomaly_score" in result.columns
    assert "is_anomaly" in result.columns


def test_scores_in_unit_interval():
    df = _make_df()
    detector = AnomalyDetector()
    detector.fit(df)
    scores = detector.score(df)
    assert scores.min() >= 0.0
    assert scores.max() <= 1.0


def test_predict_returns_boolean_series():
    df = _make_df()
    detector = AnomalyDetector()
    detector.fit(df)
    flags = detector.predict(df)
    assert flags.dtype == bool
    assert len(flags) == len(df)


def test_score_before_fit_raises():
    df = _make_df()
    detector = AnomalyDetector()
    with pytest.raises(RuntimeError, match="fit()"):
        detector.score(df)


def test_missing_feature_column_raises():
    df = _make_df().drop(columns=["density"])
    detector = AnomalyDetector()
    with pytest.raises(ValueError, match="density"):
        detector.fit(df)


def test_threshold_controls_anomaly_rate():
    df = _make_df(n=500)
    detector = AnomalyDetector(contamination=0.1)
    detector.fit(df)
    flags_strict = detector.predict(df, threshold=0.9)
    flags_loose = detector.predict(df, threshold=0.5)
    assert flags_strict.sum() <= flags_loose.sum()
