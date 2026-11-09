# Agent Operating Instructions

## Mission

Use this repository as the authoritative local MCP adapter for OpenAI Platform model discovery and inference. Keep the experience human-friendly while allowing agents to automate model selection and execution.

## Mandatory workflow

1. Call `openai_health_check` before diagnosing authentication or connectivity.
2. Call `openai_list_models` to discover model IDs visible to the current API key.
3. Call `openai_inspect_model` before selecting a specialized endpoint or an unfamiliar model.
4. Use `openai_recommend_model` as a shortlist generator, not as a benchmark or a price oracle.
5. Call the correct endpoint-specific tool. Do not treat every model as a Responses model.
6. Inspect returned status, request ID, usage, and output artifact paths. Report errors accurately.

## Routing rules

- General text, reasoning, code, vision, and supported built-in tools: `openai_create_response`.
- Models or audio workflows requiring Chat Completions: `openai_create_chat_completion`.
- Image creation/editing: `openai_generate_image` / `openai_edit_image`.
- Recorded audio transcription: `openai_transcribe_audio`.
- Text-to-speech: `openai_generate_speech`, but first verify the requested model is currently supported by `/v1/audio/speech`.
- Vectors: `openai_create_embeddings`.
- Safety classification: `openai_moderate_content`.
- Realtime: create a short-lived client secret, then let the application establish WebRTC/WebSocket.
- GPT-Live: create a WebRTC session from an SDP offer; the client maintains the media connection.

## Model lifecycle and uncertainty

- A model ID in `/v1/models` proves visibility only; it does not prove every endpoint is supported.
- Honor `shutdown_date`. Exclude models whose shutdown date is in the past unless the user explicitly asks to inspect historical/deprecated entries.
- Never invent pricing, context windows, or capability flags. The Models API does not supply them.
- If a model is absent from the local registry, mark its capabilities as unknown and consult current official docs.
- Specialized models may require organization approval.

## Security

- Never ask the user to paste an API key into a prompt or MCP tool argument.
- Never upload a local file unless the user explicitly authorized sending it to the OpenAI Platform; the upload tool requires `confirm_upload=true`.
- Never print, log, commit, or return the primary API key.
- Do not widen the REST allowlist to arbitrary URLs, organization administration, billing, or destructive endpoints without a separate security review.
- Treat ephemeral Realtime secrets as credentials; disclose them only to the intended client and never persist them in logs.
- Keep generated files inside the configured artifacts directory.

## Project quality

- Add tests for new routing, validation, and endpoint policy behavior.
- Keep Skills in English; include Traditional Chinese trigger words in descriptions.
- Prefer concise tool results with request IDs and usage. Include raw payloads only when explicitly requested.
- Update `config/model_capabilities.json` and `docs/API-MATRIX.md` when official model capabilities change.
