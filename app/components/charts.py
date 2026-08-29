"""
charts.py -- Reusable Plotly chart helpers for the OrbitIQ dashboard.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def time_series_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str = "#3b82d4",
    zero_line: bool = False,
    title: str = "",
) -> go.Figure:
    """Return a clean Plotly line chart for a single time series.

    Args:
        df: Source DataFrame.
        x: Column name for the x-axis (datetime).
        y: Column name for the y-axis.
        color: Line colour hex string.
        zero_line: If True, draw a dashed horizontal line at y=0.
        title: Optional chart title.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x],
            y=df[y],
            mode="lines",
            line=dict(color=color, width=1.5),
            name=y,
        )
    )
    if zero_line:
        fig.add_hline(y=0, line_dash="dash", line_color="#e05c5c", opacity=0.6)

    fig.update_layout(
        title=title,
        xaxis_title="Time (UTC)",
        yaxis_title=y,
        margin=dict(l=40, r=20, t=30, b=40),
        plot_bgcolor="#f7f8fa",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
    )
    return fig


def anomaly_score_chart(
    df: pd.DataFrame,
    score_col: str = "anomaly_score",
    time_col: str = "time_tag",
    threshold: float = 0.70,
) -> go.Figure:
    """Return a Plotly chart overlaying anomaly scores with a threshold line.

    Normal readings are plotted in blue; anomalous readings in red.
    """
    normal = df[df[score_col] < threshold]
    anomalous = df[df[score_col] >= threshold]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=normal[time_col],
            y=normal[score_col],
            mode="markers",
            marker=dict(color="#3b82d4", size=3, opacity=0.6),
            name="Normal",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=anomalous[time_col],
            y=anomalous[score_col],
            mode="markers",
            marker=dict(color="#e05c5c", size=6, symbol="x"),
            name="Anomaly",
        )
    )
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="#e05c5c",
        opacity=0.7,
        annotation_text=f"Threshold ({threshold:.2f})",
        annotation_position="bottom right",
    )
    fig.update_layout(
        xaxis_title="Time (UTC)",
        yaxis_title="Anomaly Score",
        yaxis=dict(range=[0, 1.05]),
        margin=dict(l=40, r=20, t=30, b=40),
        plot_bgcolor="#f7f8fa",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
    )
    return fig
