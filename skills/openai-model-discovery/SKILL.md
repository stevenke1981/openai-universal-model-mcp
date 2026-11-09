---
name: openai-model-discovery
description: Discover, inspect, filter, and track OpenAI Platform API models and lifecycle. Trigger for model catalog, available models, model ID, model shutdown, 模型清單, 模型權限, 模型停用, or API model discovery.
---

# OpenAI Model Discovery

## Source of truth

Call `openai_list_models` for live model IDs visible to the current API key. Its default limit is 1000; check `truncated` and `total_matching` if a larger catalog is returned. Use `openai_get_model` for one record and `openai_inspect_model` to combine live metadata with the local capability registry.

## Important fields

- `id`: exact model ID to pass to an endpoint.
- `owned_by`: model owner.
- `created`: model creation timestamp.
- `shutdown_date`: announced shutdown date, when present.
- `availability_status`: locally derived lifecycle state.
- `metadata_status`: `documented` or `unknown` capability metadata.

## Rules

1. Do not use a display name when an exact model ID is required.
2. Exclude models whose shutdown date is in the past unless the user asks to inspect historical entries.
3. A future shutdown date means the model is scheduled to shut down; do not present it as a long-term default.
4. The Models API does not include all modalities, context limits, prices, or endpoint compatibility.
5. For unknown model IDs, consult the official model reference and update `config/model_capabilities.json` only with verified evidence.
6. Do not infer API availability from ChatGPT UI availability.

## Common user requests

- 「我帳號可以使用哪些模型？」 → `openai_list_models`.
- 「某個模型是否停用？」 → `openai_get_model` and inspect `shutdown_date`.
- 「這個模型支援圖片或音訊嗎？」 → `openai_inspect_model`, then official model page if metadata is unknown.
