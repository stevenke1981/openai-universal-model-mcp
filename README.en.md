# OpenAI Universal Model MCP

A dynamic MCP server and agent-skill bundle for discovering and invoking OpenAI Platform API models. It is designed for Codex, Claude Desktop, Cursor, VS Code, and other MCP hosts.

## Principles

- Discover models live through `GET /v1/models`; do not hard-code account availability.
- Supplement model IDs with a documented capability registry because the Models API does not expose full endpoint or modality metadata.
- Route each workload to the correct API surface: Responses, Chat Completions, Images, Audio, Embeddings, Moderation, Realtime, or GPT-Live.
- Treat project permissions, shutdown dates, and endpoint compatibility as runtime facts.
- Keep API keys out of tool arguments and source control.

See the Traditional Chinese `README.md` for installation, configuration, and examples.

## Quick start

```powershell
.\scripts\install.ps1
notepad .env
.\scripts\test.ps1
.\scripts\run.ps1
```

Set `OPENAI_API_KEY` in `.env` before connecting an MCP host, or keep it in the OS environment. Codex forwards only allowlisted variables to MCP servers, so an OS-level key needs `env_vars = ["OPENAI_API_KEY"]` (see `examples/codex-config.toml`). For Claude Code, run `claude mcp add --scope user openai-universal-models -- uv --directory <absolute-project-path> run python -m openai_universal_model_mcp.server`. To copy the bundled Skills into a Codex-style skills directory, run `scripts/install-skills.ps1` and pass `-TargetPath` for other runtimes.

## Tool inventory

`openai_health_check`, `openai_list_models`, `openai_get_model`, `openai_inspect_model`, `openai_recommend_model`, `openai_upload_file`, `openai_create_response`, `openai_create_chat_completion`, `openai_generate_image`, `openai_edit_image`, `openai_transcribe_audio`, `openai_generate_speech`, `openai_create_embeddings`, `openai_moderate_content`, `openai_create_realtime_client_secret`, `openai_create_live_session`, and `openai_safe_api_request`.

The server exposes `openai://model-capabilities` and the `choose_openai_model` prompt.

## Reliable startup

Start the stdio server from the project root with `uv run python -m openai_universal_model_mcp.server`. For the MCP Inspector, run `uv run mcp dev src/openai_universal_model_mcp/server.py --with-editable .` to make package imports resolvable.

## Important

This project targets the OpenAI Platform API, not ChatGPT's consumer model selector. The API key only sees models and features enabled for its project. A model listed by `/v1/models` may still be shut down or unavailable on a specific endpoint. Realtime and GPT-Live tools create connection credentials or an SDP answer; a client application must maintain the actual media connection.
