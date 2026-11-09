---
name: openai-model-routing
description: Route a task to an OpenAI model and compatible API endpoint. Trigger for model selection, reasoning effort, cost/quality tradeoffs, model router, 模型推薦, 模型路由, 推理強度, or endpoint selection.
---

# OpenAI Model Routing

## Decision sequence

1. Classify the task: general, reasoning, coding, vision, image generation/editing, transcription, realtime, embeddings, moderation, cyber, or life sciences.
2. Call `openai_recommend_model(task, budget_preference)`.
3. Inspect the selected ID with `openai_inspect_model`.
4. Confirm endpoint and input/output modalities.
5. Set effort and output limits only when supported.
6. Execute and report model ID, endpoint, usage, and request ID.

## Task priorities

| Task | Starting preference | Endpoint |
|---|---|---|
| Complex reasoning | GPT-6 Astra or GPT-6.1 Sol | Responses |
| Coding/agentic work | GPT-6.1 Sol or Astra | Responses |
| Fast visual reasoning/writing | GPT-6.1 Terra | Responses |
| Cost-sensitive text work | GPT-6 Luna | Responses |
| Image generation/editing | GPT Image 2.6 Sunburst/Flare | Images |
| Recorded transcription | GPT-Transcribe | Audio Transcriptions |
| Realtime speech | GPT-Realtime family | Realtime |
| Full-duplex delegated voice | GPT-Live 1 | Live |
| Embeddings | text-embedding-3-large/small | Embeddings |
| Moderation | omni-moderation-latest | Moderations |

These are starting points, not guarantees. The live model list and project access decide availability.

## Fallback policy

- If a preferred model is not visible, select an available documented alternative.
- If an endpoint rejects a model, do not silently switch API surfaces; inspect the error and model docs.
- For 429, respect retry-after and project limits.
- For 401/403, stop and explain the authentication or permission blocker.
- For timeout on a billable request, do not automatically replay it; the first request may have completed.
