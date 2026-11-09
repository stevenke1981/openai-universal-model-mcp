"""Model capability metadata and conservative recommendation logic."""
from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = PROJECT_ROOT / "config" / "model_capabilities.json"


def load_registry() -> dict[str, Any]:
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"models": [], "metadata": {"status": "registry_unavailable"}}


def model_metadata(model_id: str) -> dict[str, Any]:
    registry = load_registry()
    for item in registry.get("models", []):
        if item.get("id") == model_id:
            return dict(item)
    return {
        "id": model_id,
        "family": "unknown",
        "kind": "unknown",
        "capabilities": [],
        "input_modalities": [],
        "output_modalities": [],
        "endpoints": [],
        "metadata_status": "unknown",
        "notes": "The API model list does not expose capability metadata. Verify the official model page before selecting an endpoint.",
    }


def availability_status(model: dict[str, Any], today: date | None = None) -> str:
    today = today or datetime.now(UTC).date()
    shutdown = model.get("shutdown_date")
    if not shutdown:
        return "listed_no_shutdown_date"
    try:
        shutdown_day = date.fromisoformat(str(shutdown)[:10])
    except ValueError:
        return "listed_shutdown_date_unparsed"
    if shutdown_day <= today:
        return "shutdown_or_past_shutdown_date"
    return "scheduled_shutdown"


TASK_PRIORITY: dict[str, list[str]] = {
    "reasoning": ["gpt-6-astra", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna"],
    "coding": ["gpt-6.1-sol", "gpt-6-astra", "gpt-6-sol", "gpt-6-luna"],
    "general": ["gpt-6.1-sol", "gpt-6.1-terra", "gpt-6-luna", "gpt-6-astra"],
    "vision": ["gpt-6.1-terra", "gpt-6-astra", "gpt-6.1-sol"],
    "image_generation": ["gpt-image-2.6-sunburst", "gpt-image-2.6-flare", "gpt-image-2.5-sunburst", "gpt-image-2.5-flare"],
    "image_editing": ["gpt-image-2.6-sunburst", "gpt-image-2.5-sunburst", "gpt-image-2.6-flare"],
    "transcription": ["gpt-transcribe", "gpt-live-transcribe", "gpt-realtime-whisper"],
    "realtime": ["gpt-realtime-2.1", "gpt-realtime-2.1-mini", "gpt-live-1", "gpt-realtime-2"],
    "embeddings": ["text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"],
    "moderation": ["omni-moderation-latest"],
    "cyber": ["gpt-6-cyber", "gpt-5.6-cyber"],
    "life_sciences": ["gpt-rosalind"],
}

QUALITY_ORDER = {
    "reasoning": ["gpt-6-astra", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna"],
    "coding": ["gpt-6-astra", "gpt-6.1-sol", "gpt-6-sol", "gpt-6-luna"],
    "general": ["gpt-6-astra", "gpt-6.1-sol", "gpt-6.1-terra", "gpt-6-luna"],
    "vision": ["gpt-6.1-terra", "gpt-6-astra", "gpt-6.1-sol"],
    "image_generation": ["gpt-image-2.6-sunburst", "gpt-image-2.6-flare", "gpt-image-2.5-sunburst"],
    "image_editing": ["gpt-image-2.6-sunburst", "gpt-image-2.6-flare", "gpt-image-2.5-sunburst"],
    "transcription": ["gpt-transcribe", "gpt-live-transcribe", "gpt-realtime-whisper"],
    "realtime": ["gpt-realtime-2.1", "gpt-live-1", "gpt-realtime-2"],
    "embeddings": ["text-embedding-3-large", "text-embedding-3-small"],
    "moderation": ["omni-moderation-latest"],
    "cyber": ["gpt-6-cyber", "gpt-5.6-cyber"],
    "life_sciences": ["gpt-rosalind"],
}

LOW_COST_ORDER = {
    "reasoning": ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"],
    "coding": ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"],
    "general": ["gpt-6-luna", "gpt-6.1-terra", "gpt-6.1-sol", "gpt-6-astra"],
    "vision": ["gpt-6.1-terra", "gpt-6.1-sol", "gpt-6-astra"],
}


def recommend_from_models(models: list[dict[str, Any]], task: str, budget: str = "balanced") -> dict[str, Any]:
    normalized = task.strip().lower().replace("-", "_").replace(" ", "_")
    priorities = TASK_PRIORITY.get(normalized)
    if not priorities:
        return {
            "ok": False,
            "task": task,
            "message": "Task category is not recognized. Use reasoning, coding, general, vision, image_generation, image_editing, transcription, realtime, embeddings, moderation, cyber, or life_sciences.",
        }
    by_id = {item.get("id"): item for item in models if item.get("id")}
    if budget == "low" and normalized in LOW_COST_ORDER:
        priorities = LOW_COST_ORDER[normalized] + [x for x in priorities if x not in LOW_COST_ORDER[normalized]]
    elif budget == "quality" and normalized in QUALITY_ORDER:
        priorities = QUALITY_ORDER[normalized] + [x for x in priorities if x not in QUALITY_ORDER[normalized]]
    available = []
    unavailable = []
    for model_id in priorities:
        item = by_id.get(model_id)
        if not item:
            unavailable.append(model_id)
            continue
        status = availability_status(item)
        if status == "shutdown_or_past_shutdown_date":
            unavailable.append(model_id)
            continue
        meta = model_metadata(model_id)
        available.append({
            "id": model_id,
            "status": status,
            "kind": meta.get("kind"),
            "endpoints": meta.get("endpoints", []),
            "capabilities": meta.get("capabilities", []),
        })
    if not available:
        return {
            "ok": False,
            "task": normalized,
            "message": "No preferred model is visible to this API key. Check project access or use openai_list_models to select another model.",
            "not_visible_or_shutdown": unavailable,
        }
    return {
        "ok": True,
        "task": normalized,
        "budget_preference": budget,
        "recommended": available[0],
        "alternatives": available[1:],
        "not_visible_or_shutdown": unavailable,
        "selection_note": "This is a conservative catalog-based recommendation, not a live benchmark or guaranteed price comparison. Verify endpoint compatibility with openai_inspect_model.",
    }
