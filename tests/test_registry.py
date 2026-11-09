from datetime import date

from openai_universal_model_mcp.registry import (
    availability_status,
    model_metadata,
    recommend_from_models,
)


def test_availability_status_shutdown_and_scheduled():
    assert availability_status({"shutdown_date": "2026-01-01"}, date(2026, 11, 8)) == "shutdown_or_past_shutdown_date"
    assert availability_status({"shutdown_date": "2027-01-01"}, date(2026, 11, 8)) == "scheduled_shutdown"
    assert availability_status({"shutdown_date": None}, date(2026, 11, 8)) == "listed_no_shutdown_date"


def test_unknown_model_is_not_assigned_guessed_endpoint():
    metadata = model_metadata("brand-new-model-x")
    assert metadata["metadata_status"] == "unknown"
    assert metadata["endpoints"] == []


def test_recommendation_uses_only_visible_models():
    models = [
        {"id": "gpt-6.1-sol", "shutdown_date": None},
        {"id": "gpt-6-astra", "shutdown_date": "2026-01-01"},
    ]
    result = recommend_from_models(models, "reasoning", "balanced")
    assert result["ok"] is True
    assert result["recommended"]["id"] == "gpt-6.1-sol"
    assert "gpt-6-astra" in result["not_visible_or_shutdown"]


def test_unknown_task_is_rejected():
    result = recommend_from_models([], "telepathy", "balanced")
    assert result["ok"] is False
