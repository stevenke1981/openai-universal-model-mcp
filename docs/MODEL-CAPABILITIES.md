# Model Capability Snapshot

Verified: 2026-11-08

This file is a human-readable companion to `config/model_capabilities.json`. It is a reviewed capability snapshot, not a guarantee that every listed model is enabled for every API project. The live `GET /v1/models` response is authoritative for API-key visibility.

## General-purpose GPT models

| Model ID | Capabilities | API surfaces | Notes |
|---|---|---|---|
| `gpt-6-astra` | text_generation, reasoning, coding, vision, tool_calling | responses | Flagship reasoning and complex coding model. |
| `gpt-6.1-sol` | text_generation, reasoning, coding, vision, tool_calling | responses | Near-flagship quality with lower cost than Astra. |
| `gpt-6.1-terra` | text_generation, reasoning, coding, vision, tool_calling | responses | Visual reasoning, computer use, and writing. |
| `gpt-6-luna` | text_generation, reasoning, coding, vision, tool_calling | responses | Efficient model for high-volume workloads. |
| `gpt-6-sol` | text_generation, reasoning, coding, vision, tool_calling | responses | Coding and agentic workflows. |
| `gpt-5.6-sol` | text_generation, reasoning, coding, vision, tool_calling | responses | Professional reasoning and coding. |
| `gpt-5.6-terra` | text_generation, reasoning, coding, vision, tool_calling | responses | Balanced model for visual reasoning and tools. |
| `gpt-5.6-luna` | text_generation, reasoning, coding, vision, tool_calling | responses | Cost-sensitive high-volume workloads. |
| `gpt-5.5` | text_generation, reasoning, coding, vision, tool_calling | responses | General professional work and coding. |
| `gpt-5.5-pro` | text_generation, reasoning, coding, vision, tool_calling | responses | Higher-precision professional work. |
| `gpt-5.4` | text_generation, reasoning, coding, vision, tool_calling | responses | General professional work and coding. |
| `gpt-5.4-pro` | text_generation, reasoning, coding, vision, tool_calling | responses | Higher-precision professional work. |
| `gpt-5.4-mini` | text_generation, reasoning, coding, vision, tool_calling | responses | Efficient coding, computer use, and subagents. |
| `gpt-5.2` | text_generation, reasoning, coding, vision, tool_calling | responses | Reasoning model with configurable effort. |
| `gpt-5.2-pro` | text_generation, reasoning, coding, vision, tool_calling | responses | Higher-precision reasoning. |
| `gpt-oss-120b` | text_generation, reasoning, coding, vision, tool_calling | responses | Open-weight model; verify hosted API availability for your project. |
| `gpt-oss-20b` | text_generation, reasoning, coding, vision, tool_calling | responses | Open-weight model; verify hosted API availability for your project. |

## Specialized models

| Model ID | Capabilities | API surfaces | Notes |
|---|---|---|---|
| `gpt-6-cyber` | cybersecurity_reasoning, authorized_defensive_security | responses | Restricted cybersecurity access program; eligibility and access controls apply. |
| `gpt-5.6-cyber` | cybersecurity_reasoning, authorized_defensive_security | responses | Restricted cybersecurity model; eligibility and access controls apply. |
| `gpt-rosalind` | life_sciences_reasoning | responses | Access is restricted to approved organizations. |

## Image models

| Model ID | Capabilities | API surfaces | Notes |
|---|---|---|---|
| `gpt-image-2.6-sunburst` | image_generation, image_editing, svg_output, animated_gif_output, complexity_control | images/generations, images/edits | Image generation and editing; high-detail workflows. Supports complexity control, SVG output, and animated GIF output according to the current official Image 2.6 guide. |
| `gpt-image-2.6-flare` | image_generation, image_editing, svg_output, animated_gif_output, complexity_control | images/generations, images/edits | Image generation and editing; fast iteration. Supports complexity control, SVG output, and animated GIF output according to the current official Image 2.6 guide. |
| `gpt-image-2.5-sunburst` | image_generation, image_editing | images/generations, images/edits | Image generation and editing; precision-oriented. |
| `gpt-image-2.5-flare` | image_generation, image_editing | images/generations, images/edits | Image generation and editing; fast everyday generation. |
| `gpt-image-2` | image_generation, image_editing | images/generations, images/edits | Image generation and editing; confirm the current model alias and endpoint support. |
| `gpt-image-1` | image_generation, image_editing | images/generations, images/edits | [shutdown] Shut down on 2026-10-23; use a current GPT Image model. |
| `gpt-image-1.5` | image_generation, image_editing | images/generations, images/edits | [deprecated] Deprecated prior image model; prefer GPT Image 2.6 or 2.5. |
| `gpt-image-1-mini` | image_generation, image_editing | images/generations, images/edits | [deprecated] Deprecated prior image model; prefer a current GPT Image model. |

## Audio and realtime models

| Model ID | Capabilities | API surfaces | Notes |
|---|---|---|---|
| `gpt-live-1` | realtime_audio, speech_to_speech, streaming | live/sessions | Full-duplex Live voice session; uses the Live WebRTC/sideband session API. |
| `gpt-realtime-2.1` | realtime_audio, speech_to_speech, streaming | realtime/client_secrets, realtime | Realtime speech, reasoning, and tool use. |
| `gpt-realtime-2.1-mini` | realtime_audio, speech_to_speech, streaming | realtime/client_secrets, realtime | Realtime speech, reasoning, and tool use in a smaller model. |
| `gpt-realtime-2` | realtime_audio, speech_to_speech, streaming | realtime/client_secrets, realtime | Realtime speech and reasoning. |
| `gpt-realtime-1.5` | realtime_audio, speech_to_speech, streaming | realtime/client_secrets, realtime | Realtime audio input/output. |
| `gpt-realtime-translate` | realtime_audio, speech_to_speech, streaming | realtime/translations/client_secrets, realtime/translations | Realtime speech-to-speech translation. |
| `gpt-live-transcribe` | realtime_audio, speech_to_speech, streaming | realtime/client_secrets, realtime/transcription_sessions | Low-latency realtime speech transcription. |
| `gpt-realtime-whisper` | realtime_audio, speech_to_speech, streaming | realtime/client_secrets, realtime/transcription_sessions | Realtime transcription model. |
| `gpt-transcribe` | speech_to_text, file_transcription | audio/transcriptions, realtime/client_secrets | Recommended starting point for recorded audio transcription. |
| `gpt-audio-1.5` | audio_input, audio_output | chat/completions | Use Chat Completions audio parameters; verify current model access. |
| `gpt-4o-mini-tts` | text_to_speech | audio/speech | [deprecated] Legacy speech-generation model; check the official deprecation page and current endpoint availability before new deployments. |
| `tts-1` | text_to_speech | audio/speech | [deprecated] Deprecated legacy speech model; do not choose for new workflows without explicit user instruction. |
| `tts-1-hd` | text_to_speech | audio/speech | [deprecated] Deprecated legacy speech model; do not choose for new workflows without explicit user instruction. |

## Embedding models

| Model ID | Capabilities | API surfaces | Notes |
|---|---|---|---|
| `text-embedding-3-large` | text_embeddings | embeddings | Highest capability embedding model in the current catalog. |
| `text-embedding-3-small` | text_embeddings | embeddings | Smaller, lower-cost embedding model. |
| `text-embedding-ada-002` | text_embeddings | embeddings | Legacy embedding model; prefer text-embedding-3 models for new work. |

## Moderation models

| Model ID | Capabilities | API surfaces | Notes |
|---|---|---|---|
| `omni-moderation-latest` | text_moderation, image_moderation | moderations | Moderation endpoint; interpret scores as signals, not an automatic policy decision. |

## ChatGPT product-only models

| Model ID | Capabilities | API surfaces | Notes |
|---|---|---|---|
| `chat-latest` | — | Not recommended for API | ChatGPT model; official model catalog says it is not recommended for API use. |
| `chatgpt-image-latest` | — | Not recommended for API | [deprecated] ChatGPT image model; not a general API image model. Use a documented GPT Image API model. |

## Operating rules

- Use `openai_list_models` to discover the models visible to the configured project API key.
- Use `openai_inspect_model` to join live visibility with capability metadata.
- Do not infer endpoint support for a model whose `metadata_status` is `unknown`.
- Do not select models marked `api_use_recommended=false` for API calls.
- Exclude models whose shutdown date is in the past; treat future shutdown dates as migration warnings.
- Prices, context windows, and rate limits are intentionally not copied into this static registry because they change and are not returned by the Models API.

## Official sources

- https://developers.openai.com/api/docs/models/all
- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/reference/resources/models/methods/list
- https://developers.openai.com/api/reference/resources/models/methods/retrieve
- https://developers.openai.com/api/reference/resources/responses/methods/create
- https://developers.openai.com/api/docs/guides/image-generation
- https://developers.openai.com/api/docs/models/gpt-image-2.6-sunburst
- https://developers.openai.com/api/docs/models/gpt-image-2.6-flare
- https://developers.openai.com/api/docs/guides/transcription
- https://developers.openai.com/api/docs/guides/embeddings
- https://developers.openai.com/api/docs/guides/moderation
- https://developers.openai.com/api/reference/resources/realtime/subresources/translations/subresources/client_secrets/methods/create
- https://developers.openai.com/api/docs/guides/realtime-translation
- https://developers.openai.com/api/reference/resources/live/methods/create
