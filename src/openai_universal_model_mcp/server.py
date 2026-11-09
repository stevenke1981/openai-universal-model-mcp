"""OpenAI Platform Universal Model MCP server (MCP Python SDK v2)."""
from __future__ import annotations

import base64
import json
import mimetypes
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

from openai_universal_model_mcp.api import request_binary, request_json
from openai_universal_model_mcp.config import API_BASE_URL, api_key, artifact_dir
from openai_universal_model_mcp.registry import (
    availability_status,
    load_registry,
    model_metadata,
    recommend_from_models,
)
from openai_universal_model_mcp.security import (
    output_path,
    parse_json_object_or_array,
    validate_api_endpoint,
    validate_local_file,
    validate_model_id,
)

mcp = MCPServer("OpenAI Universal Model MCP")


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _save_image_items(data: dict[str, Any], filename_prefix: str, extension: str) -> list[dict[str, str]]:
    saved: list[dict[str, str]] = []
    items = data.get("data", []) if isinstance(data, dict) else []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        encoded = item.get("b64_json")
        if encoded:
            name = f"{filename_prefix}_{index}.{extension}"
            target = output_path(name, extension, artifact_dir())
            target.write_bytes(base64.b64decode(encoded))
            saved.append({"path": str(target), "format": extension})
        elif item.get("url"):
            saved.append({"url": str(item["url"]), "format": extension})
    return saved


def _summarize_output_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for item in response.get("output", []) if isinstance(response, dict) else []:
        if not isinstance(item, dict):
            continue
        summary: dict[str, Any] = {"type": item.get("type")}
        for key in ("id", "status", "name", "call_id", "arguments", "role", "code", "container_id"):
            if key in item:
                value = item[key]
                summary[key] = value[:6000] if isinstance(value, str) else value
        if item.get("type") == "message":
            text_parts = []
            for content in item.get("content", []) or []:
                if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                    if isinstance(content.get("text"), str):
                        text_parts.append(content["text"][:12000])
            if text_parts:
                summary["text"] = "\n".join(text_parts)
        if item.get("type") == "image_generation_call":
            summary["image_result_present"] = bool(item.get("result"))
            if item.get("revised_prompt"):
                summary["revised_prompt"] = str(item["revised_prompt"])[:3000]
        if item.get("type") in {"web_search_call", "computer_call", "code_interpreter_call"}:
            if item.get("action"):
                summary["action"] = item["action"]
        summaries.append(summary)
    return summaries


def _extract_response_text(response: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in response.get("output", []) if isinstance(response, dict) else []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []) or []:
            if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                text = content.get("text")
                if isinstance(text, str):
                    parts.append(text)
    return "\n".join(parts).strip()


@mcp.tool()
async def openai_health_check() -> dict[str, Any]:
    """Check local configuration and connectivity to the OpenAI Platform API."""
    if not api_key():
        return {
            "ok": False,
            "configured": False,
            "message": "OPENAI_API_KEY is missing.",
            "next_step": "Create a project API key, place it in the project .env file, then restart the MCP server.",
        }
    result = await request_json("GET", "models")
    if not result.get("ok"):
        return {"ok": False, "configured": True, "api_reachable": False, "details": result}
    return {
        "ok": True,
        "configured": True,
        "api_reachable": True,
        "api_base": API_BASE_URL,
        "visible_model_sample_count": len(result.get("data", {}).get("data", [])),
        "message": "OpenAI Platform API authentication succeeded.",
    }


@mcp.tool()
async def openai_list_models(
    query: str = "",
    include_shutdown: bool = False,
    limit: int = 1000,
) -> dict[str, Any]:
    """List model IDs visible to this API key. Filter shutdown models unless explicitly requested."""
    limit = max(1, min(int(limit), 1000))
    result = await request_json("GET", "models")
    if not result.get("ok"):
        return result
    payload = result.get("data", {})
    models = payload.get("data", []) if isinstance(payload, dict) else []
    today = datetime.now(UTC).date()
    filtered = []
    q = query.strip().lower()
    for item in models:
        if not isinstance(item, dict):
            continue
        status = availability_status(item, today)
        if not include_shutdown and status == "shutdown_or_past_shutdown_date":
            continue
        if q and q not in str(item.get("id", "")).lower() and q not in str(item.get("owned_by", "")).lower():
            continue
        filtered.append({
            "id": item.get("id"),
            "owned_by": item.get("owned_by"),
            "created": item.get("created"),
            "shutdown_date": item.get("shutdown_date"),
            "availability_status": status,
            "known_capabilities": model_metadata(str(item.get("id", ""))).get("capabilities", []),
            "metadata_status": model_metadata(str(item.get("id", ""))).get("metadata_status", "unknown"),
        })
    total_matching = len(filtered)
    filtered = filtered[:limit]
    return {
        "ok": True,
        "count": len(filtered),
        "total_matching": total_matching,
        "truncated": total_matching > limit,
        "models": filtered,
        "include_shutdown": include_shutdown,
        "note": "The /models endpoint returns identifiers and basic metadata, not a complete capability or pricing specification.",
        "request_id": result.get("request_id"),
    }


@mcp.tool()
async def openai_get_model(model_id: str) -> dict[str, Any]:
    """Retrieve one model record from GET /v1/models/{model_id}."""
    try:
        model_id = validate_model_id(model_id)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json("GET", f"models/{model_id}")
    if not result.get("ok"):
        return result
    return {"ok": True, "model": result.get("data"), "availability_status": availability_status(result.get("data", {})), "request_id": result.get("request_id")}


@mcp.tool()
async def openai_inspect_model(model_id: str) -> dict[str, Any]:
    """Inspect live API visibility plus locally documented capabilities and compatible endpoints."""
    try:
        model_id = validate_model_id(model_id)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json("GET", f"models/{model_id}")
    if not result.get("ok"):
        return result
    model = result.get("data", {})
    metadata = model_metadata(model_id)
    return {
        "ok": True,
        "model": model,
        "availability_status": availability_status(model),
        "capabilities": metadata,
        "selection_guidance": (
            "This is a ChatGPT product model and is not recommended for API use. Choose an API model from the official catalog."
            if metadata.get("api_use_recommended") is False
            else "Use the listed endpoint(s) only after checking the model page and project permissions."
            if metadata.get("metadata_status") == "documented"
            else "Model is visible, but capability metadata is unknown. Verify the official model page before selecting an endpoint."
        ),
        "request_id": result.get("request_id"),
    }


@mcp.tool()
async def openai_recommend_model(task: str, budget_preference: str = "balanced") -> dict[str, Any]:
    """Recommend an available model for a supported task using the live model list and curated priorities."""
    if budget_preference not in {"low", "balanced", "quality"}:
        return {"ok": False, "error": "budget_preference must be low, balanced, or quality."}
    result = await request_json("GET", "models")
    if not result.get("ok"):
        return result
    models = result.get("data", {}).get("data", [])
    recommendation = recommend_from_models(models, task, budget_preference)
    recommendation["request_id"] = result.get("request_id")
    return recommendation


@mcp.tool()
async def openai_upload_file(
    file_path: str,
    confirm_upload: bool = False,
) -> dict[str, Any]:
    """Upload a local file to OpenAI Files for Responses input. Requires explicit confirm_upload=true."""
    if not confirm_upload:
        return {"ok": False, "confirmation_required": True, "message": "This uploads and stores a local file in the OpenAI Platform project. Set confirm_upload=true only after the user explicitly authorizes this upload."}
    try:
        local_file = validate_local_file(file_path, max_bytes=50 * 1024 * 1024)
        mime = mimetypes.guess_type(local_file.name)[0] or "application/octet-stream"
        with local_file.open("rb") as handle:
            result = await request_json(
                "POST",
                "files",
                data={"purpose": "user_data"},
                files={"file": (local_file.name, handle, mime)},
            )
    except (ValueError, OSError) as exc:
        return {"ok": False, "error": str(exc)}
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    return {
        "ok": True,
        "file": {
            "id": data.get("id"),
            "filename": data.get("filename"),
            "purpose": data.get("purpose"),
            "bytes": data.get("bytes"),
            "expires_at": data.get("expires_at"),
        },
        "request_id": result.get("request_id"),
        "note": "Use the returned file ID in a Responses API input_file or input_image item when supported. File retention follows the OpenAI Platform file policy.",
    }


@mcp.tool()
async def openai_create_response(
    model: str,
    input_text: str = "",
    input_json: str = "",
    instructions: str = "",
    reasoning_effort: str = "",
    max_output_tokens: int = 0,
    temperature: float = -1.0,
    tools_json: str = "",
    tool_choice_json: str = "",
    text_format_json: str = "",
    previous_response_id: str = "",
    store: bool = False,
    safety_identifier: str = "",
    include_raw: bool = False,
) -> dict[str, Any]:
    """Call the Responses API for text, reasoning, image input, tools, or structured output."""
    try:
        model = validate_model_id(model)
        body: dict[str, Any] = {"model": model, "store": store}
        if input_json.strip():
            parsed_input = parse_json_object_or_array(input_json, "input_json")
            if not isinstance(parsed_input, (list, str)):
                return {"ok": False, "error": "input_json must contain a JSON array or string."}
            body["input"] = parsed_input
        elif input_text:
            body["input"] = input_text
        else:
            return {"ok": False, "error": "Provide input_text or input_json."}
        if instructions:
            body["instructions"] = instructions
        if reasoning_effort:
            if reasoning_effort not in {"none", "minimal", "low", "medium", "high", "xhigh", "max"}:
                return {"ok": False, "error": "Unsupported reasoning_effort value."}
            supported_efforts = model_metadata(model).get("reasoning_effort_levels", [])
            if supported_efforts and reasoning_effort not in supported_efforts:
                return {"ok": False, "error": f"{model} documents reasoning effort values: {', '.join(supported_efforts)}."}
            body["reasoning"] = {"effort": reasoning_effort}
        if max_output_tokens > 0:
            body["max_output_tokens"] = min(max_output_tokens, 128000)
        if temperature >= 0:
            body["temperature"] = min(max(temperature, 0.0), 2.0)
        if tools_json.strip():
            tools = parse_json_object_or_array(tools_json, "tools_json")
            if not isinstance(tools, list):
                return {"ok": False, "error": "tools_json must contain a JSON array."}
            body["tools"] = tools
        if tool_choice_json.strip():
            body["tool_choice"] = parse_json_object_or_array(tool_choice_json, "tool_choice_json")
        if text_format_json.strip():
            body["text"] = {"format": parse_json_object_or_array(text_format_json, "text_format_json")}
        if previous_response_id:
            if not store:
                return {"ok": False, "error": "Set store=true when continuing with previous_response_id."}
            body["previous_response_id"] = previous_response_id
        if safety_identifier:
            body["safety_identifier"] = safety_identifier[:128]
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    result = await request_json("POST", "responses", json_body=body)
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    answer = {
        "ok": True,
        "id": data.get("id"),
        "model": data.get("model", model),
        "status": data.get("status"),
        "output_text": _extract_response_text(data),
        "output_items": _summarize_output_items(data),
        "usage": data.get("usage"),
        "request_id": result.get("request_id"),
    }
    if include_raw:
        answer["raw"] = data
    return answer


@mcp.tool()
async def openai_create_chat_completion(
    model: str,
    messages_json: str,
    max_completion_tokens: int = 0,
    temperature: float = -1.0,
    modalities_json: str = "",
    audio_json: str = "",
    response_format_json: str = "",
    save_audio_output: bool = True,
) -> dict[str, Any]:
    """Call Chat Completions for models or audio workflows that require that API surface."""
    try:
        model = validate_model_id(model)
        messages = parse_json_object_or_array(messages_json, "messages_json")
        if not isinstance(messages, list):
            return {"ok": False, "error": "messages_json must be a JSON array."}
        body: dict[str, Any] = {"model": model, "messages": messages}
        if max_completion_tokens > 0:
            body["max_completion_tokens"] = min(max_completion_tokens, 128000)
        if temperature >= 0:
            body["temperature"] = min(max(temperature, 0.0), 2.0)
        if modalities_json.strip():
            modalities = parse_json_object_or_array(modalities_json, "modalities_json")
            if not isinstance(modalities, list):
                return {"ok": False, "error": "modalities_json must contain a JSON array."}
            body["modalities"] = modalities
        if audio_json.strip():
            body["audio"] = parse_json_object_or_array(audio_json, "audio_json")
        if response_format_json.strip():
            body["response_format"] = parse_json_object_or_array(response_format_json, "response_format_json")
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json("POST", "chat/completions", json_body=body)
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    choices = data.get("choices", [])
    first = choices[0] if choices else {}
    message = dict(first.get("message", {})) if isinstance(first, dict) and isinstance(first.get("message", {}), dict) else {}
    audio_info = None
    audio_payload = message.get("audio")
    if isinstance(audio_payload, dict) and audio_payload.get("data"):
        audio_payload = dict(audio_payload)
        encoded_audio = audio_payload.pop("data")
        if save_audio_output:
            audio_format = str(audio_payload.get("format", "wav")).lower()
            if audio_format not in {"mp3", "opus", "aac", "flac", "wav", "pcm"}:
                audio_format = "wav"
            target = output_path(f"chat_audio_{_timestamp()}.{audio_format}", audio_format, artifact_dir())
            try:
                target.write_bytes(base64.b64decode(encoded_audio))
                audio_info = {"path": str(target), "format": audio_format, "bytes": target.stat().st_size}
            except (ValueError, OSError) as exc:
                audio_info = {"saved": False, "error": str(exc)}
        else:
            audio_info = {"saved": False, "note": "Audio bytes omitted because save_audio_output=false."}
        message["audio"] = audio_payload
    return {
        "ok": True,
        "id": data.get("id"),
        "model": data.get("model", model),
        "message": message,
        "audio_file": audio_info,
        "finish_reason": first.get("finish_reason") if isinstance(first, dict) else None,
        "usage": data.get("usage"),
        "request_id": result.get("request_id"),
    }


@mcp.tool()
async def openai_generate_image(
    model: str,
    prompt: str,
    size: str = "auto",
    quality: str = "auto",
    background: str = "auto",
    output_format: str = "png",
    n: int = 1,
    complexity: str = "",
    moderation: str = "auto",
    frame_count: int = 0,
    frame_duration_ms: int = 0,
    output_compression: int = -1,
    safety_identifier: str = "",
    filename_prefix: str = "openai_image",
) -> dict[str, Any]:
    """Generate images with GPT Image 2.x; supports 2.6 complexity and GIF frame controls."""
    try:
        model = validate_model_id(model)
        if not prompt.strip():
            return {"ok": False, "error": "prompt is required."}
        if output_format not in {"png", "jpeg", "webp", "gif", "svg"}:
            return {"ok": False, "error": "output_format must be png, jpeg, webp, gif, or svg."}
        if complexity and complexity not in {"low", "medium", "high"}:
            return {"ok": False, "error": "complexity must be low, medium, or high."}
        if complexity and not model.startswith("gpt-image-2.6-"):
            return {"ok": False, "error": "complexity is documented for GPT Image 2.6 models only."}
        if moderation not in {"auto", "low"}:
            return {"ok": False, "error": "moderation must be auto or low."}
        if output_format == "svg" and n != 1:
            return {"ok": False, "error": "SVG generation requires n=1."}
        if output_format == "gif" and frame_count and not 2 <= frame_count <= 16:
            return {"ok": False, "error": "GIF frame_count must be between 2 and 16."}
        if output_format != "gif" and (frame_count or frame_duration_ms):
            return {"ok": False, "error": "frame_count and frame_duration_ms are only valid with output_format=gif."}
        if output_compression >= 0 and output_format not in {"jpeg", "webp"}:
            return {"ok": False, "error": "output_compression is only supported for jpeg and webp."}
        body: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "background": background,
            "output_format": output_format,
            "moderation": moderation,
            "n": max(1, min(int(n), 10)),
        }
        if complexity:
            body["complexity"] = complexity
        if output_format == "gif":
            if frame_count:
                body["frame_count"] = frame_count
            if frame_duration_ms:
                normalized_duration = max(20, min(int(frame_duration_ms), 2000))
                body["frame_duration_ms"] = max(20, min(((normalized_duration + 5) // 10) * 10, 2000))
        if output_compression >= 0:
            body["output_compression"] = max(0, min(int(output_compression), 100))
        if safety_identifier:
            if len(safety_identifier) > 128:
                return {"ok": False, "error": "safety_identifier must be 128 characters or fewer."}
            body["safety_identifier"] = safety_identifier
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json("POST", "images/generations", json_body=body)
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    saved = _save_image_items(data, f"{filename_prefix}_{_timestamp()}", output_format)
    return {
        "ok": True,
        "model": model,
        "created": data.get("created"),
        "requested_options": {"size": size, "quality": quality, "background": background, "output_format": output_format, "complexity": complexity or None, "moderation": moderation, "frame_count": frame_count or None, "frame_duration_ms": frame_duration_ms or None, "output_compression": output_compression if output_compression >= 0 else None},
        "saved_images": saved,
        "count": len(saved),
        "usage": data.get("usage"),
        "request_id": result.get("request_id"),
        "note": "Generated image files are saved locally under OPENAI_ARTIFACT_DIR.",
    }


@mcp.tool()
async def openai_edit_image(
    model: str,
    image_path: str,
    prompt: str,
    mask_path: str = "",
    size: str = "auto",
    quality: str = "auto",
    background: str = "auto",
    output_format: str = "png",
    complexity: str = "",
    frame_count: int = 0,
    frame_duration_ms: int = 0,
    output_compression: int = -1,
    safety_identifier: str = "",
    filename: str = "openai_edited_image",
) -> dict[str, Any]:
    """Edit one local image with a GPT Image model. An optional alpha mask may be supplied."""
    try:
        model = validate_model_id(model)
        image_file = validate_local_file(image_path, max_bytes=50 * 1024 * 1024)
        if not prompt.strip():
            return {"ok": False, "error": "prompt is required."}
        if output_format not in {"png", "jpeg", "webp", "gif"}:
            return {"ok": False, "error": "Image edits support png, jpeg, webp, or gif; SVG is generation-only."}
        if complexity and (complexity not in {"low", "medium", "high"} or not model.startswith("gpt-image-2.6-")):
            return {"ok": False, "error": "complexity must be low, medium, or high and is documented for GPT Image 2.6 models only."}
        if output_format == "gif" and frame_count and not 2 <= frame_count <= 16:
            return {"ok": False, "error": "GIF frame_count must be between 2 and 16."}
        if output_format != "gif" and (frame_count or frame_duration_ms):
            return {"ok": False, "error": "frame_count and frame_duration_ms are only valid with output_format=gif."}
        if output_compression >= 0 and output_format not in {"jpeg", "webp"}:
            return {"ok": False, "error": "output_compression is only supported for jpeg and webp."}
        body = {"model": model, "prompt": prompt, "size": size, "quality": quality, "background": background, "output_format": output_format}
        if complexity:
            body["complexity"] = complexity
        if output_format == "gif":
            if frame_count:
                body["frame_count"] = frame_count
            if frame_duration_ms:
                normalized_duration = max(20, min(int(frame_duration_ms), 2000))
                body["frame_duration_ms"] = max(20, min(((normalized_duration + 5) // 10) * 10, 2000))
        if output_compression >= 0:
            body["output_compression"] = max(0, min(int(output_compression), 100))
        if safety_identifier:
            if len(safety_identifier) > 128:
                return {"ok": False, "error": "safety_identifier must be 128 characters or fewer."}
            body["safety_identifier"] = safety_identifier
        mime = mimetypes.guess_type(image_file.name)[0] or "application/octet-stream"
        with image_file.open("rb") as handle:
            upload_files: list[tuple[str, tuple[str, Any, str]]] = [("image", (image_file.name, handle, mime))]
            if mask_path:
                mask_file = validate_local_file(mask_path, max_bytes=50 * 1024 * 1024)
                mask_mime = mimetypes.guess_type(mask_file.name)[0] or "application/octet-stream"
                with mask_file.open("rb") as mask_handle:
                    upload_files.append(("mask", (mask_file.name, mask_handle, mask_mime)))
                    result = await request_json("POST", "images/edits", data=body, files=upload_files)
            else:
                result = await request_json("POST", "images/edits", data=body, files=upload_files)
    except (ValueError, OSError) as exc:
        return {"ok": False, "error": str(exc)}
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    saved = _save_image_items(data, f"{Path(filename).stem}_{_timestamp()}", output_format)
    return {"ok": True, "model": model, "saved_images": saved, "count": len(saved), "request_id": result.get("request_id")}


@mcp.tool()
async def openai_transcribe_audio(
    file_path: str,
    model: str = "gpt-transcribe",
    response_format: str = "json",
    language: str = "",
    prompt: str = "",
) -> dict[str, Any]:
    """Transcribe a local audio/video file using the Audio Transcriptions API."""
    try:
        model = validate_model_id(model)
        audio_file = validate_local_file(file_path, max_bytes=25 * 1024 * 1024)
        if response_format not in {"json", "text", "srt", "vtt", "verbose_json", "diarized_json"}:
            return {"ok": False, "error": "Unsupported response_format."}
        data = {"model": model, "response_format": response_format}
        if language:
            data["language"] = language
        if prompt:
            data["prompt"] = prompt
        mime = mimetypes.guess_type(audio_file.name)[0] or "application/octet-stream"
        with audio_file.open("rb") as handle:
            result = await request_binary("POST", "audio/transcriptions", data=data, files={"file": (audio_file.name, handle, mime)})
    except (ValueError, OSError) as exc:
        return {"ok": False, "error": str(exc)}
    if not result.get("ok"):
        return result
    raw = result.get("content", b"")
    content_type = result.get("content_type", "")
    if "json" in content_type or response_format in {"json", "verbose_json", "diarized_json"}:
        try:
            transcript: Any = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            transcript = raw.decode("utf-8", errors="replace")
    else:
        transcript = raw.decode("utf-8", errors="replace")
    return {"ok": True, "model": model, "transcript": transcript, "request_id": result.get("request_id")}


@mcp.tool()
async def openai_generate_speech(
    model: str,
    input_text: str,
    voice: str = "alloy",
    response_format: str = "mp3",
    speed: float = 1.0,
    instructions: str = "",
    filename: str = "openai_speech",
) -> dict[str, Any]:
    """Generate speech audio and save it locally. Supply a model supported by the current speech endpoint."""
    try:
        model = validate_model_id(model)
        if not input_text.strip():
            return {"ok": False, "error": "input_text is required."}
        if response_format not in {"mp3", "opus", "aac", "flac", "wav", "pcm"}:
            return {"ok": False, "error": "Unsupported response_format."}
        body: dict[str, Any] = {"model": model, "input": input_text, "voice": voice, "response_format": response_format, "speed": min(max(speed, 0.25), 4.0)}
        if instructions:
            body["instructions"] = instructions
        result = await request_binary("POST", "audio/speech", json_body=body)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    if not result.get("ok"):
        return result
    target = output_path(f"{Path(filename).stem}_{_timestamp()}.{response_format}", response_format, artifact_dir())
    target.write_bytes(result.get("content", b""))
    return {"ok": True, "model": model, "path": str(target), "bytes": target.stat().st_size, "request_id": result.get("request_id")}


@mcp.tool()
async def openai_create_embeddings(
    model: str,
    input_text: str = "",
    input_json: str = "",
    dimensions: int = 0,
    include_vectors: bool = False,
) -> dict[str, Any]:
    """Create text embeddings. Vector values are omitted by default to keep MCP responses compact."""
    try:
        model = validate_model_id(model)
        if input_json.strip():
            embedding_input = parse_json_object_or_array(input_json, "input_json")
            if not isinstance(embedding_input, (list, str)):
                return {"ok": False, "error": "input_json must contain a JSON array or string."}
        elif input_text:
            embedding_input = input_text
        else:
            return {"ok": False, "error": "Provide input_text or input_json."}
        if dimensions < 0:
            return {"ok": False, "error": "dimensions must be zero or a positive integer."}
        body: dict[str, Any] = {"model": model, "input": embedding_input, "encoding_format": "float"}
        if dimensions > 0:
            body["dimensions"] = dimensions
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json("POST", "embeddings", json_body=body)
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    vectors = []
    for item in data.get("data", []) if isinstance(data, dict) else []:
        vector = item.get("embedding", []) if isinstance(item, dict) else []
        row: dict[str, Any] = {"index": item.get("index"), "dimensions": len(vector)}
        if include_vectors:
            row["embedding"] = vector
        vectors.append(row)
    return {"ok": True, "model": data.get("model", model), "vectors": vectors, "usage": data.get("usage"), "request_id": result.get("request_id"), "vectors_included": include_vectors}


@mcp.tool()
async def openai_moderate_content(
    input_text: str = "",
    input_json: str = "",
    model: str = "omni-moderation-latest",
) -> dict[str, Any]:
    """Classify text or supported image inputs with the Moderations API."""
    try:
        model = validate_model_id(model)
        if input_json.strip():
            moderation_input = parse_json_object_or_array(input_json, "input_json")
        elif input_text:
            moderation_input = input_text
        else:
            return {"ok": False, "error": "Provide input_text or input_json."}
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json("POST", "moderations", json_body={"model": model, "input": moderation_input})
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    return {"ok": True, "model": data.get("model", model), "results": data.get("results", []), "request_id": result.get("request_id")}


@mcp.tool()
async def openai_create_realtime_client_secret(
    model: str = "gpt-realtime-2.1",
    session_type: str = "",
    session_json: str = "",
    expires_in_seconds: int = 600,
    safety_identifier: str = "",
) -> dict[str, Any]:
    """Create a short-lived Realtime client secret. The main API key is never returned."""
    try:
        model = validate_model_id(model)
        expires_in_seconds = max(10, min(int(expires_in_seconds), 7200))
        if session_json.strip():
            session = parse_json_object_or_array(session_json, "session_json")
            if not isinstance(session, dict):
                return {"ok": False, "error": "session_json must contain a JSON object."}
            effective_model = validate_model_id(str(session.get("model") or model))
        else:
            session = {}
            effective_model = model
        if effective_model == "gpt-realtime-translate":
            return {"ok": False, "error": "Use openai_create_realtime_translation_secret for gpt-realtime-translate."}
        if not session_type:
            session_type = "transcription" if effective_model in {"gpt-transcribe", "gpt-live-transcribe", "gpt-realtime-whisper"} else "realtime"
        if session_type not in {"realtime", "transcription"}:
            return {"ok": False, "error": "session_type must be realtime or transcription."}
        session.setdefault("type", session_type)
        session.setdefault("model", effective_model)
        if effective_model == "gpt-realtime-whisper" and session_type == "transcription":
            audio = session.setdefault("audio", {})
            if isinstance(audio, dict):
                audio_input = audio.setdefault("input", {})
                if isinstance(audio_input, dict):
                    audio_input.setdefault("turn_detection", None)
        body = {"expires_after": {"anchor": "created_at", "seconds": expires_in_seconds}, "session": session}
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json("POST", "realtime/client_secrets", json_body=body, safety_identifier=safety_identifier)
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    return {"ok": True, "client_secret": data.get("value"), "expires_at": data.get("expires_at"), "session": data.get("session"), "request_id": result.get("request_id"), "warning": "Treat client_secret as a short-lived credential. Do not log or commit it."}


@mcp.tool()
async def openai_create_realtime_translation_secret(
    session_json: str,
    expires_in_seconds: int = 600,
    safety_identifier: str = "",
) -> dict[str, Any]:
    """Create a short-lived client secret for the Realtime Translation API."""
    try:
        session = parse_json_object_or_array(session_json, "session_json")
        if not isinstance(session, dict):
            return {"ok": False, "error": "session_json must contain a JSON object."}
        if not session.get("model"):
            session["model"] = "gpt-realtime-translate"
        if session.get("model") != "gpt-realtime-translate":
            return {"ok": False, "error": "This tool is reserved for gpt-realtime-translate."}
        expires_in_seconds = max(10, min(int(expires_in_seconds), 7200))
        body = {"expires_after": {"anchor": "created_at", "seconds": expires_in_seconds}, "session": session}
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json("POST", "realtime/translations/client_secrets", json_body=body, safety_identifier=safety_identifier)
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    return {"ok": True, "client_secret": data.get("value"), "expires_at": data.get("expires_at"), "session": data.get("session"), "request_id": result.get("request_id"), "warning": "Treat client_secret as a short-lived credential. Do not log or commit it."}


@mcp.tool()
async def openai_create_live_session(
    sdp_offer: str,
    session_json: str = "",
    model: str = "gpt-live-1",
    safety_identifier: str = "",
) -> dict[str, Any]:
    """Create a GPT-Live WebRTC session from an SDP offer and return the SDP answer."""
    try:
        model = validate_model_id(model)
        if not sdp_offer.strip():
            return {"ok": False, "error": "sdp_offer is required."}
        if session_json.strip():
            session = parse_json_object_or_array(session_json, "session_json")
            if not isinstance(session, dict):
                return {"ok": False, "error": "session_json must contain a JSON object."}
            session.setdefault("model", model)
        else:
            session = {"model": model}
        body = {"session": session, "transport": {"type": "webrtc", "sdp": sdp_offer}}
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json("POST", "live/sessions", json_body=body, safety_identifier=safety_identifier)
    if not result.get("ok"):
        return result
    data = result.get("data", {})
    return {"ok": True, "session": data.get("session"), "transport": data.get("transport"), "request_id": result.get("request_id"), "note": "This creates the session and SDP answer. Your WebRTC client must complete the peer connection and carry the live audio stream."}


@mcp.tool()
async def openai_safe_api_request(
    method: str,
    path: str,
    body_json: str = "",
    query_json: str = "",
) -> dict[str, Any]:
    """Advanced JSON REST call restricted to approved model and inference endpoints; no destructive methods."""
    try:
        method, path = validate_api_endpoint(method, path)
        body = parse_json_object_or_array(body_json, "body_json") if body_json.strip() else None
        query = parse_json_object_or_array(query_json, "query_json") if query_json.strip() else None
        if query is not None and not isinstance(query, dict):
            return {"ok": False, "error": "query_json must contain a JSON object."}
        if body is not None and not isinstance(body, (dict, list)):
            return {"ok": False, "error": "body_json must contain a JSON object or array."}
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    result = await request_json(method, path, params=query, json_body=body)
    if not result.get("ok"):
        return result
    return {"ok": True, "path": path, "method": method, "data": result.get("data"), "request_id": result.get("request_id")}


@mcp.resource("openai://model-capabilities")
def openai_model_capabilities_resource() -> str:
    """Read the local capability registry snapshot and its official source links."""
    return json.dumps(load_registry(), ensure_ascii=False, indent=2)


@mcp.prompt()
def choose_openai_model(task: str, constraints: str = "") -> str:
    """Create a model-selection prompt that requires live discovery and endpoint validation."""
    return (
        "Select an OpenAI Platform model for this task. First call openai_list_models, then "
        "openai_recommend_model and openai_inspect_model. Never assume every model supports "
        "the same endpoint. Check shutdown_date, project access, input/output modalities, "
        "reasoning effort support, and the task's cost/latency constraints.\n\n"
        f"Task: {task}\nConstraints: {constraints or 'Not specified'}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
