## 0.1.2 — 2026-11-09

- Document Claude Code registration and the Codex `env_vars` setting for OS-level API keys.
- Exclude local caches and build metadata from Git; keep file bytes stable so `SHA256SUMS.txt` verifies on any clone.
- Apply Ruff import-order and `datetime.UTC` fixes.

## 0.1.1 — 2026-11-08

- Fix MCP server package imports for CLI-based loading.
- Add direct `python -m openai_universal_model_mcp.server` stdio entrypoint.
- Update Windows launcher and host configurations to use the module entrypoint.
- Document the editable install flag needed by the Inspector development sandbox.

# Changelog

## 0.1.0 — 2026-11-08

- Initial dynamic model discovery and model lifecycle filtering.
- Capability registry snapshot based on the official OpenAI model catalog.
- MCP tools for Responses, Chat Completions, Images, Audio, Embeddings, Moderation, Realtime, and GPT-Live setup.
- Safe inference endpoint allowlist for advanced REST requests.
- Seven agent-first Skills and Codex/Claude/Cursor configuration examples.
- Unit tests for routing metadata and input safety.
