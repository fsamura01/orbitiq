"""
granite_client.py -- IBM Granite (watsonx.ai) NL explanation & Q&A client.

Required environment variables (see .env.example):
    WATSONX_API_KEY
    WATSONX_PROJECT_ID
    WATSONX_URL
    GRANITE_MODEL_ID
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _load_env() -> Dict[str, str]:
    required = ("WATSONX_API_KEY", "WATSONX_PROJECT_ID", "WATSONX_URL", "GRANITE_MODEL_ID")
    config: Dict[str, str] = {}
    missing = []
    for key in required:
        value = os.getenv(key)
        if not value:
            missing.append(key)
        else:
            config[key] = value
    if missing:
        raise EnvironmentError(
            f"Missing env vars: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in your credentials."
        )
    return config


class GraniteClient:
    """Thin watsonx.ai wrapper for OrbitIQ natural language tasks.

    Two capabilities:
      - explain_anomaly()  : plain-English summary of a detected anomaly
      - answer_question()  : grounded Q&A against live telemetry context
    """

    def __init__(self) -> None:
        config = _load_env()
        self._project_id = config["WATSONX_PROJECT_ID"]
        self._model_id = config["GRANITE_MODEL_ID"]
        self._client = self._init_client(config)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def explain_anomaly(self, anomaly_stats: Dict[str, Any], max_new_tokens: int = 300) -> str:
        """Generate a plain-English explanation for a detected anomaly.

        Args:
            anomaly_stats: Dict with keys: timestamp, speed, density,
                temperature, bt, bz_gsm, anomaly_score.
        """
        prompt = self._build_explanation_prompt(anomaly_stats)
        return self._generate(prompt, max_new_tokens=max_new_tokens)

    def answer_question(self, question: str, telemetry_context: str, max_new_tokens: int = 400) -> str:
        """Answer an operator question grounded in the telemetry context."""
        prompt = self._build_qa_prompt(question, telemetry_context)
        return self._generate(prompt, max_new_tokens=max_new_tokens)

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_explanation_prompt(stats: Dict[str, Any]) -> str:
        score = stats.get("anomaly_score", "N/A")
        score_str = f"{score:.2f}" if isinstance(score, float) else str(score)
        return (
            "You are OrbitIQ, an AI assistant for spacecraft mission health monitoring. "
            "A machine learning model has detected an anomaly in NASA satellite telemetry. "
            "Explain what this anomaly means in plain English and describe the potential "
            "impact on spacecraft systems and mission safety. Keep your response concise "
            "(3-5 sentences) and suitable for a mission operations engineer.\n\n"
            f"Anomaly details:\n"
            f"  Timestamp       : {stats.get('timestamp', 'unknown')}\n"
            f"  Solar wind speed: {stats.get('speed', 'N/A')} km/s\n"
            f"  Proton density  : {stats.get('density', 'N/A')} n/cm3\n"
            f"  Temperature     : {stats.get('temperature', 'N/A')} K\n"
            f"  Magnetic field  : {stats.get('bt', 'N/A')} nT total, "
            f"Bz = {stats.get('bz_gsm', 'N/A')} nT\n"
            f"  Anomaly score   : {score_str} / 1.00\n\n"
            "Explanation:"
        )

    @staticmethod
    def _build_qa_prompt(question: str, context: str) -> str:
        return (
            "You are OrbitIQ, an AI assistant for spacecraft mission health monitoring. "
            "Answer the operator question using only the provided telemetry context. "
            "If the context does not contain enough information, say so clearly.\n\n"
            f"Current telemetry context:\n{context}\n\n"
            f"Operator question: {question}\n\n"
            "Answer:"
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _init_client(config: Dict[str, str]) -> Any:
        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference

            credentials = Credentials(
                url=config["WATSONX_URL"],
                api_key=config["WATSONX_API_KEY"],
            )
            model = ModelInference(
                model_id=config["GRANITE_MODEL_ID"],
                credentials=credentials,
                project_id=config["WATSONX_PROJECT_ID"],
            )
            logger.info("Granite client ready (model: %s).", config["GRANITE_MODEL_ID"])
            return model
        except ImportError as exc:
            raise ImportError(
                "ibm-watsonx-ai is not installed. Run: pip install ibm-watsonx-ai"
            ) from exc

    def _generate(self, prompt: str, max_new_tokens: int = 300, retries: int = 3) -> str:
        """Call Granite with simple exponential backoff on 429 rate-limit errors."""
        for attempt in range(1, retries + 1):
            try:
                result = self._client.generate_text(
                    prompt=prompt,
                    params={"max_new_tokens": max_new_tokens, "temperature": 0.3},
                )
                return result.strip()
            except Exception as exc:
                msg = str(exc)
                is_rate_limit = "429" in msg or "consumption_limit_reached" in msg
                if is_rate_limit and attempt < retries:
                    wait = 2 ** attempt  # 2s, 4s
                    logger.warning("Rate limit hit, retrying in %ds (attempt %d/%d)...", wait, attempt, retries)
                    time.sleep(wait)
                    continue
                if is_rate_limit:
                    logger.error("Rate limit exhausted after %d attempts.", retries)
                    raise RateLimitError(
                        "The free watsonx plan concurrent request limit has been reached. "
                        "Wait a few seconds and try again."
                    ) from exc
                logger.error("Granite generation failed: %s", exc)
                raise


class RateLimitError(Exception):
    """Raised when the watsonx API returns a 429 rate-limit response."""
