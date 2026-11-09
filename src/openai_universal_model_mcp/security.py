"""Input validation and local file handling."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def parse_json_object_or_array(raw: str, field_name: str) -> Any:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field_name} must be valid JSON: {exc.msg}") from exc
    if not isinstance(value, (dict, list, str, int, float, bool)) and value is not None:
        raise ValueError(f"{field_name} must be a JSON value")
    return value


def validate_model_id(model_id: str) -> str:
    value = model_id.strip()
    if not MODEL_ID_RE.fullmatch(value):
        raise ValueError("Invalid model_id. Use the exact model ID returned by openai_list_models.")
    return value


def validate_local_file(file_path: str, *, max_bytes: int | None = None) -> Path:
    path = Path(file_path).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    if max_bytes is not None and path.stat().st_size > max_bytes:
        raise ValueError(f"File exceeds the configured size limit of {max_bytes} bytes: {path.name}")
    return path


def output_path(filename: str, extension: str, output_dir: Path) -> Path:
    ext = extension.lower().lstrip(".")
    if not re.fullmatch(r"[a-z0-9]{1,8}", ext):
        raise ValueError("Invalid output extension")
    raw = Path(filename).name if filename else ""
    stem = Path(raw).stem if raw else ""
    stem = FILENAME_RE.sub("_", stem).strip("._-") or "openai_output"
    stem = stem[:80]
    candidate = (output_dir / f"{stem}.{ext}").resolve()
    if candidate.parent != output_dir.resolve():
        raise ValueError("Output filename must stay inside the configured artifact directory")
    return candidate


def validate_api_endpoint(method: str, path: str) -> tuple[str, str]:
    """Restrict advanced REST access to known inference and model-discovery endpoints."""
    verb = method.upper().strip()
    clean = path.strip().lstrip("/")
    if clean.startswith("v1/"):
        clean = clean[3:]
    if not clean or any(token in clean for token in ("..", "?", "#", "\\", "://")):
        raise ValueError("Use a relative API path without query strings, traversal, or a URL")
    if verb == "GET":
        if clean == "models":
            return verb, clean
        if clean.startswith("models/"):
            validate_model_id(clean.split("/", 1)[1])
            return verb, clean
    allowed_post = {
        "responses",
        "chat/completions",
        "images/generations",
        "embeddings",
        "moderations",
        "realtime/client_secrets",
        "realtime/translations/client_secrets",
        "live/sessions",
    }
    if verb == "POST" and clean in allowed_post:
        return verb, clean
    raise ValueError(
        "Endpoint is not in the safe inference allowlist. Allowed: model discovery and supported inference endpoints."
    )
