---
name: openai-api-extension
description: Extend the MCP server to new OpenAI Platform endpoints while preserving least privilege. Trigger for new API endpoints, endpoint adapters, platform features, API 擴充, 新增模型 API, or MCP 工具擴充.
---

# Safe API Extension

## Extension checklist

1. Confirm the endpoint exists in the current official OpenAI API reference.
2. Identify its HTTP method, request schema, response schema, model eligibility, and side effects.
3. Classify whether it is inference, read-only discovery, lifecycle mutation, administration, or billing.
4. Add a dedicated MCP tool for a stable workflow rather than exposing arbitrary HTTP.
5. Add strict typed inputs, file size bounds, output containment, normalized errors, and request IDs.
6. Add unit tests for input validation, endpoint policy, and error handling.
7. Update `docs/API-MATRIX.md`, the capability registry if needed, and the relevant Skills.
8. Keep credentials in environment variables and avoid logging request bodies that may contain user data.

## Default deny

Do not add arbitrary URLs, arbitrary host overrides, organization administration, API-key management, billing, destructive operations, or unbounded file operations to the inference MCP server.

## Unknown models

A newly listed model must remain `metadata_status=unknown` until official documentation confirms its modalities and endpoint support. The API may be tried only when the user explicitly requests it and the failure mode is clearly reported.
