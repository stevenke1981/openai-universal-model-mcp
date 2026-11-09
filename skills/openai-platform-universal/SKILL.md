---
name: openai-platform-universal
description: Operate the OpenAI Platform Universal Model MCP. Trigger for OpenAI API, Platform models, model calls, GPT selection, API usage, 模型清單, 呼叫模型, OpenAI 平台, or MCP model routing.
---

# OpenAI Platform Universal Model MCP

## Purpose

Use the OpenAI Platform through the local `openai-universal-model-mcp` server. This skill coordinates discovery, model selection, endpoint routing, execution, and result validation.

## Required workflow

1. Run `openai_health_check` when connection or authentication is uncertain.
2. Run `openai_list_models` to discover models visible to the active API key.
3. For model choice, call `openai_recommend_model` and then `openai_inspect_model`.
4. Select the endpoint based on the task and documented model capabilities.
5. If local file input is needed, obtain explicit user authorization before calling `openai_upload_file` with `confirm_upload=true`.
6. Execute one endpoint-specific tool and inspect its status, request ID, usage, and artifact path.
6. Report any permission, endpoint, deprecation, or quota limitation without guessing.

## Endpoint map

- Reasoning, text, code, vision, tools: `openai_create_response`.
- Chat Completions-only or compatible audio flows: `openai_create_chat_completion`.
- Image creation/editing: `openai_generate_image` / `openai_edit_image`.
- Recorded audio transcription: `openai_transcribe_audio`.
- Speech generation: `openai_generate_speech` after checking current model support.
- Embeddings: `openai_create_embeddings`.
- Content classification: `openai_moderate_content`.
- Realtime voice: `openai_create_realtime_client_secret` followed by an application-owned media connection.
- GPT-Live: `openai_create_live_session` with a browser-generated SDP offer.

## Model-selection policy

- Prefer current models with documented endpoint support.
- Use `balanced` as the default budget preference; use `low` for cost-sensitive work and `quality` when quality dominates.
- Use `reasoning_effort` only when supported by the selected model.
- Do not assume a model supports every tool, modality, or endpoint.
- A model visible in `/v1/models` is not proof that every endpoint is enabled.
- If `metadata_status=unknown`, consult the official model page before calling.

## Cost and data policy

- API calls may incur Platform charges. Never claim ChatGPT plan usage and API usage are interchangeable.
- Keep output-token limits and image counts intentional.
- The default Responses request uses `store=false`.
- Do not log or expose API keys or ephemeral credentials.

## Chinese-language intent examples

- 「列出我可以用的所有模型」 → `openai_list_models`.
- 「用最強推理模型分析」 → discovery → recommendation → inspect → Responses.
- 「幫我生圖／改圖」 → Image tool.
- 「把錄音轉成字幕」 → transcription.
- 「即時語音翻譯」 → Realtime/Live setup; explain that a client must own the media stream.
