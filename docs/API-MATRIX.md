# API Capability Matrix

Snapshot date: 2026-11-08. This is an implementation guide, not a promise that every project has access to every model.

| Model family | Typical task | API surface | MCP entry point | Important boundary |
|---|---|---|---|---|
| GPT-6 / GPT-5.x general models | Text, reasoning, code, vision, tools | Responses | `openai_create_response` | Per-model tool and reasoning support still varies. |
| GPT-6 / GPT-5.x models requiring Chat Completions | Chat-compatible workflows | Chat Completions | `openai_create_chat_completion` | Use the current model reference. |
| GPT Image 2.6 / 2.5 / 2 | Generate/edit images, SVG generation, GIF generation/editing | Images API or Responses image-generation tool | `openai_generate_image`, `openai_edit_image` | 2.6 supports complexity control; SVG is generation-only and requires `n=1`; GIF supports 2–16 frames and 20–2000 ms per frame. |
| GPT-Transcribe | Recorded speech-to-text | Audio Transcriptions | `openai_transcribe_audio` | Upload size and supported formats are endpoint-specific. |
| Speech models | Text-to-speech | Audio Speech | `openai_generate_speech` | Supply a model currently supported by the endpoint; legacy TTS IDs may be deprecated. |
| GPT-Realtime | Realtime audio sessions | Realtime client secrets + WebRTC/WebSocket | `openai_create_realtime_client_secret` | The client must maintain the media connection. |
| GPT-Live | Full-duplex Live voice | Live WebRTC | `openai_create_live_session` | Requires an SDP offer; tool returns SDP answer, not the media stream. |
| Embedding models | Vectorization | Embeddings | `openai_create_embeddings` | Return vectors only when `include_vectors=true`. |
| Moderation | Text/image classification | Moderations | `openai_moderate_content` | Scores are signals; do not blindly automate enforcement. |
| Cyber / Life Sciences | Specialized reasoning | Usually Responses | `openai_create_response` | Organization/project eligibility may be required. |
| Open-weight models | General inference where hosted access exists | Model-specific | `openai_create_response` | Catalog listing and API project access must both be verified. |

## Not included in this initial MCP scope

- Fine-tuning job management
- Batch job lifecycle and file management
- Evals and graders
- Vector store/file search administration
- Organization, project, API-key, billing, and audit administration
- Arbitrary third-party compatible endpoints

These are Platform capabilities, but they are not required to call model inference endpoints. Add them as separate MCP modules with dedicated permissions and tests rather than expanding the inference server's privileges.
