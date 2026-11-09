# OpenAI Universal Model MCP

**OpenAI Platform 的通用模型 MCP + Agent Skills 專案。** 以動態探索為核心，讓 Codex、Claude Desktop、Cursor、VS Code 及其他 MCP Host 可以使用同一個 MCP Server 呼叫帳號有權限使用的 OpenAI API 模型。

> 專案版本：0.1.2 · 文件與能力登錄檔核對日期：2026-11-08

## 設計目標

1. **不硬編碼可用模型清單**：每次透過 `GET /v1/models` 取得目前 API Key 可見的模型。
2. **能力與端點分離**：Models API 不會提供完整能力規格，因此以官方文件建立能力登錄檔，未知模型一律標示 `unknown`，不猜測。
3. **依任務選擇 API**：Responses、Chat Completions、Images、Audio、Embeddings、Moderation、Realtime、GPT-Live 各自使用正確端點。
4. **尊重帳號權限**：模型可見不等於所有端點都可用；實際呼叫由 API 權限驗證。
5. **安全預設**：API Key 只從環境變數或本機 `.env` 讀取；不接受工具參數傳入 Key；產生檔案限制在 artifact 目錄；進階 REST 工具採 endpoint allowlist。
6. **Agent-first / Human-friendly**：MCP tools 供代理呼叫，Skills 提供選型規則，人類可以用 PowerShell 和 MCP Inspector 驗證。

## 功能總覽

| Area | MCP tools | API surface |
|---|---|---|
| Discovery | `openai_list_models`, `openai_get_model`, `openai_inspect_model` | `/v1/models` |
| Routing | `openai_recommend_model` | Live model list + capability registry |
| File input | `openai_upload_file` (explicit confirmation required) | `/v1/files` |
| Text / reasoning / vision | `openai_create_response` | `/v1/responses` |
| Chat/audio-compatible models | `openai_create_chat_completion` | `/v1/chat/completions` |
| Image generation | `openai_generate_image` | `/v1/images/generations` |
| Image editing | `openai_edit_image` | `/v1/images/edits` |
| File transcription | `openai_transcribe_audio` | `/v1/audio/transcriptions` |
| Speech generation | `openai_generate_speech` | `/v1/audio/speech` |
| Embeddings | `openai_create_embeddings` | `/v1/embeddings` |
| Moderation | `openai_moderate_content` | `/v1/moderations` |
| Realtime | `openai_create_realtime_client_secret` | `/v1/realtime/client_secrets` |
| Realtime translation | `openai_create_realtime_translation_secret` | `/v1/realtime/translations/client_secrets` |
| GPT-Live | `openai_create_live_session` | `/v1/live/sessions` |
| Advanced | `openai_safe_api_request` | Allowlisted inference endpoints only |
| Diagnostics | `openai_health_check` | `/v1/models` |

The server also exposes the `openai://model-capabilities` resource and `choose_openai_model` prompt.

## 1. Requirements

- Windows 10/11, macOS, or Linux
- Python 3.11+
- `uv` package manager (recommended)
- An OpenAI Platform project API key with the required model permissions and billing configured

This is an **API integration**, not a bridge to ChatGPT's consumer model selector. ChatGPT product access does not automatically make every ChatGPT model available through the API; the official catalog explicitly separates ChatGPT-only models from API-recommended models. API usage is subject to the Platform project, endpoint permissions, rate limits, and API billing. Eligible ChatGPT Pro and Business subscriptions may claim separate API credits by linking an eligible subscription to an API organization; those credits do not expand ChatGPT or signed-in Codex usage limits.

## 2. Install on Windows (PowerShell)

Unzip the project, open PowerShell in the project directory, then run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install.ps1
```

The installer runs `uv sync --extra dev` and creates `.env` from `.env.example` if needed.

Edit `.env`:

```powershell
notepad .env
```

Set your key:

```dotenv
OPENAI_API_KEY=sk-proj-REPLACE_WITH_YOUR_KEY
OPENAI_TIMEOUT_SECONDS=180
OPENAI_ARTIFACT_DIR=artifacts
```

Do not put a real key in Git, screenshots, prompts, or MCP tool arguments.

## 3. Verify API access

```powershell
.\scripts\test.ps1
.\scripts\run.ps1
```

For an interactive tool test (requires Node.js/npx for MCP Inspector):

```powershell
uv run mcp dev src/openai_universal_model_mcp/server.py --with-editable .
```

Call `openai_health_check`, then `openai_list_models`. Use `openai_inspect_model` before selecting a model for a non-standard endpoint.

## 4. Connect to Codex

Copy the example from `examples/codex-config.toml` into your Codex `config.toml`, and replace the project directory with the actual absolute path.

Example:

```toml
[mcp_servers.openai_universal_models]
command = "uv"
args = [
  "--directory",
  "D:\\AI\\openai-universal-model-mcp",
  "run",
  "python",
  "-m",
  "openai_universal_model_mcp.server"
]
# Codex does not forward arbitrary environment variables to MCP servers.
# Needed only when the key is in the OS environment instead of .env.
env_vars = ["OPENAI_API_KEY"]
```

The recommended launch command is `uv run python -m openai_universal_model_mcp.server`. This avoids package-relative imports failing when a server file is loaded as a standalone script.

Restart Codex after editing the MCP configuration. The MCP process reads the `.env` file in the project root; a key already set in the process environment takes precedence.

## 5. Connect to Claude Code / Claude Desktop / Cursor / VS Code

Claude Code (user scope, available in every project):

```powershell
claude mcp add --scope user openai-universal-models -- uv --directory D:/path/to/openai-universal-model-mcp run python -m openai_universal_model_mcp.server
claude mcp list
```

For the other hosts, see:

- `examples/claude-desktop-config.json`
- `examples/cursor-mcp.json`

Replace the example path with the absolute project path. Host configuration formats can vary by version; keep the command and arguments aligned with the host's current MCP documentation.

## 6. Agent usage examples

### Find all visible models

```text
Call openai_list_models with include_shutdown=false.
```

### Select a reasoning model

```text
Call openai_recommend_model(task="reasoning", budget_preference="balanced").
Then call openai_inspect_model with the recommended model ID.
```

### Use a model directly

```text
Call openai_create_response:
- model: gpt-6.1-sol
- input_text: Explain Rust ownership with a small example.
- reasoning_effort: medium
- max_output_tokens: 1200
```

### Generate an image

```text
Call openai_generate_image:
- model: gpt-image-2.6-sunburst
- prompt: A cinematic photorealistic miniature greenhouse at dawn.
- size: auto
- quality: high
- output_format: png
```

The generated file is written to `artifacts/` by default. GPT Image 2.6 supports complexity controls, SVG output, and animated GIF output. For a 16-frame GIF at 120 ms per frame, set `output_format=gif`, `frame_count=16`, `frame_duration_ms=120`, and optionally `complexity=high`. The Image API accepts GIF output for generation and edits; SVG is generation-only and requires `n=1`.

```text
Call openai_generate_image:
- model: gpt-image-2.6-sunburst
- prompt: A seamless looping cinematic chibi character animation, fixed camera, consistent character and background.
- output_format: gif
- frame_count: 16
- frame_duration_ms: 120
- complexity: high
```

### Use a local PDF or image as model input

First call `openai_upload_file` with `confirm_upload=true` only after the user explicitly authorizes sending the file to OpenAI Platform. Then reference the returned `file_id` in `openai_create_response` using the appropriate `input_file` or `input_image` item.

### Analyze an image with a general model

Use `openai_create_response` with `input_json` containing a Responses API message whose content includes `input_text` and `input_image`. Supply a supported HTTPS image URL, a `data:` URL, or a previously uploaded file ID. For example:

```json
[
  {
    "role": "user",
    "content": [
      {"type": "input_text", "text": "Describe this image."},
      {"type": "input_image", "image_url": "https://example.com/image.jpg", "detail": "high"}
    ]
  }
]
```

### Transcribe audio

```text
Call openai_transcribe_audio:
- file_path: D:\\recordings\\meeting.wav
- model: gpt-transcribe
- response_format: json
```

### Create embeddings

```text
Call openai_create_embeddings:
- model: text-embedding-3-small
- input_text: The source text to embed.
- include_vectors: false
```

## 7. Skills

Skills are in `skills/`. They are written in English for consistent agent execution and include Traditional Chinese trigger phrases so Chinese-language users can invoke them naturally.

- `openai-platform-universal`: main routing and operating policy
- `openai-model-discovery`: dynamic catalog and lifecycle checks
- `openai-model-routing`: task-to-model and endpoint selection
- `openai-image-generation`: image creation and editing
- `openai-audio-realtime`: transcription, speech, Realtime, GPT-Live
- `openai-embeddings-safety`: embeddings and moderation
- `openai-api-extension`: safe extension policy for new endpoints

Use `AGENTS.md` as the project-level instruction file for coding agents. To install the bundled skills into a Codex-style skills directory, run `.\scripts\install-skills.ps1` or pass an explicit `-TargetPath` for another agent runtime.

## 8. Important compatibility boundaries

- `/v1/models` returns model identifiers and basic fields; it does not return full modalities, context windows, pricing, or endpoint compatibility.
- A model being listed does not guarantee the current project can use every endpoint or feature.
- `shutdown_date` is checked before recommending a model. A listed model with a past shutdown date is excluded from recommendations by default.
- Unknown model IDs remain discoverable but are marked with unknown capability metadata. Do not infer endpoint compatibility from the name alone.
- Realtime and GPT-Live are persistent media sessions. MCP tools create an ephemeral client secret or return an SDP answer; the application must establish and maintain the actual WebRTC/WebSocket audio stream.
- Speech generation models and endpoint support can change. Pass a currently supported model ID and verify it against the current official audio docs.
- The safe REST tool allows only a fixed set of inference endpoints and model discovery. It does not expose destructive, organization-admin, billing, or arbitrary URL access.

## 9. Tests and quality gates

```powershell
uv run pytest
uv run ruff check .
uv run python -m compileall src
```

Unit tests cover registry status, recommendation filtering, model ID validation, endpoint allowlisting, and output path containment. Live API tests are intentionally opt-in because they can incur charges.

## 10. Official references

The model catalog and API docs change over time. Treat the following official documentation as the source of truth:

- Model catalog: https://developers.openai.com/api/docs/models/all
- API credits for eligible ChatGPT subscribers: https://developers.openai.com/api/docs/guides/chatgpt-api-credits
- Models guide: https://developers.openai.com/api/docs/models
- List models: https://developers.openai.com/api/reference/resources/models/methods/list
- Retrieve model: https://developers.openai.com/api/reference/resources/models/methods/retrieve
- Responses API: https://developers.openai.com/api/reference/resources/responses/methods/create
- Image generation: https://developers.openai.com/api/docs/guides/image-generation
- Transcription: https://developers.openai.com/api/docs/guides/transcription
- Embeddings: https://developers.openai.com/api/docs/guides/embeddings
- Moderation: https://developers.openai.com/api/docs/guides/moderation
- Realtime client secrets: https://developers.openai.com/api/reference/resources/realtime/subresources/client_secrets/methods/create
- GPT-Live session creation: https://developers.openai.com/api/reference/resources/live/methods/create
- Official MCP Python SDK: https://py.sdk.modelcontextprotocol.io/

---

**Project status:** Initial implementation package. Live model access, organization approvals, and endpoint compatibility must be verified with the user's own API key. No API calls are made during installation or unit tests.
