# Troubleshooting

## `OPENAI_API_KEY is missing`

1. Copy `.env.example` to `.env`.
2. Set `OPENAI_API_KEY` in `.env`.
3. Restart the MCP host so it launches a fresh process.
4. Call `openai_health_check`.

## 401 Unauthorized

The key may be invalid, revoked, malformed, or from the wrong project. Create or select a project API key in the OpenAI Platform dashboard. Do not put the key in a prompt or tool call.

## 403 Forbidden

The project may not have access to the model, specialized program, or endpoint. Verify organization/project access and any required approval.

## 404 Model or endpoint not found

- Call `openai_list_models`.
- Call `openai_get_model` for the exact ID.
- Check `shutdown_date`.
- Confirm the model supports the selected endpoint in its official model reference.

## 429 Rate limit or quota

Check project usage limits, model rate limits, billing, and `retry_after`. Do not retry immediately in a tight loop.

## MCP server does not start

```powershell
uv sync
uv run python -m compileall src
uv run mcp dev src/openai_universal_model_mcp/server.py
```

Check that Python 3.11+ and `uv` are on PATH. The MCP Inspector also requires Node.js/npx.

## Generated file cannot be found

Call the tool result's `path` exactly. The default directory is `<project>\artifacts`; it can be changed with `OPENAI_ARTIFACT_DIR`.

## Realtime tool returns a client secret or SDP answer but no audio

That is expected. The MCP tool prepares authentication/session setup. Your browser or application must establish WebRTC/WebSocket and send/receive media events.
