"""Small REST transport for OpenAI Platform. Uses the official API host only."""
from __future__ import annotations

from typing import Any

import httpx

from .config import API_BASE_URL, api_key, timeout_seconds


def _error_payload(response: httpx.Response) -> dict[str, Any]:
    request_id = response.headers.get("x-request-id")
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    error = payload.get("error", {}) if isinstance(payload, dict) else {}
    if not isinstance(error, dict):
        error = {"message": str(error)}
    message = error.get("message") or response.text[:700] or f"HTTP {response.status_code}"
    result: dict[str, Any] = {
        "ok": False,
        "error": {
            "status_code": response.status_code,
            "type": error.get("type"),
            "code": error.get("code"),
            "message": message,
        },
        "request_id": request_id,
    }
    retry_after = response.headers.get("retry-after")
    if retry_after:
        result["retry_after"] = retry_after
    if response.status_code == 401:
        result["hint"] = "Check OPENAI_API_KEY and ensure it belongs to the intended OpenAI Platform project."
    elif response.status_code == 403:
        result["hint"] = "The project or organization may not have permission for this model or endpoint."
    elif response.status_code == 404:
        result["hint"] = "Check the model ID, endpoint, and model shutdown status."
    elif response.status_code == 429:
        result["hint"] = "Rate limit or project quota reached. Check project limits and retry-after before retrying."
    return result


async def request_json(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | list[Any] | None = None,
    data: dict[str, Any] | None = None,
    files: Any = None,
    safety_identifier: str = "",
) -> dict[str, Any]:
    key = api_key()
    if not key:
        return {
            "ok": False,
            "error": {"type": "configuration_error", "message": "OPENAI_API_KEY is not configured."},
            "hint": "Copy .env.example to .env and set OPENAI_API_KEY, or export it in the process environment.",
        }
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    if safety_identifier:
        if len(safety_identifier) > 128:
            return {"ok": False, "error": {"type": "validation_error", "message": "safety_identifier must be 128 characters or fewer."}}
        headers["OpenAI-Safety-Identifier"] = safety_identifier
    url = f"{API_BASE_URL}/{path.lstrip('/')}"
    timeout = httpx.Timeout(timeout_seconds(), connect=15.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method.upper(), url, headers=headers, params=params, json=json_body, data=data, files=files
            )
    except httpx.TimeoutException:
        return {"ok": False, "error": {"type": "timeout", "message": "OpenAI API request timed out."}}
    except httpx.HTTPError as exc:
        return {"ok": False, "error": {"type": "network_error", "message": str(exc)[:500]}}
    if response.is_error:
        return _error_payload(response)
    try:
        payload = response.json()
    except ValueError:
        payload = {"text": response.text[:12000]}
    return {"ok": True, "data": payload, "request_id": response.headers.get("x-request-id"), "status_code": response.status_code}


async def request_binary(
    method: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    files: Any = None,
    safety_identifier: str = "",
) -> dict[str, Any]:
    key = api_key()
    if not key:
        return {
            "ok": False,
            "error": {"type": "configuration_error", "message": "OPENAI_API_KEY is not configured."},
            "hint": "Copy .env.example to .env and set OPENAI_API_KEY, or export it in the process environment.",
        }
    headers = {"Authorization": f"Bearer {key}"}
    if safety_identifier:
        if len(safety_identifier) > 128:
            return {"ok": False, "error": {"type": "validation_error", "message": "safety_identifier must be 128 characters or fewer."}}
        headers["OpenAI-Safety-Identifier"] = safety_identifier
    url = f"{API_BASE_URL}/{path.lstrip('/')}"
    timeout = httpx.Timeout(timeout_seconds(), connect=15.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method.upper(), url, headers=headers, json=json_body, data=data, files=files
            )
    except httpx.TimeoutException:
        return {"ok": False, "error": {"type": "timeout", "message": "OpenAI API request timed out."}}
    except httpx.HTTPError as exc:
        return {"ok": False, "error": {"type": "network_error", "message": str(exc)[:500]}}
    if response.is_error:
        return _error_payload(response)
    return {
        "ok": True,
        "content": response.content,
        "content_type": response.headers.get("content-type", "application/octet-stream"),
        "request_id": response.headers.get("x-request-id"),
        "status_code": response.status_code,
    }
