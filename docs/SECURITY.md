# Security Model

## Secrets

- Primary credential: `OPENAI_API_KEY` from the project `.env` or process environment.
- `.env` is ignored by Git.
- The key is never a tool parameter and is never included in success or error responses.
- Realtime client secrets are short-lived credentials and must be treated as secrets.

## Network

- The HTTP client targets `https://api.openai.com/v1` only.
- The advanced REST tool accepts only an explicit endpoint allowlist.
- No arbitrary URL, path traversal, DELETE, PUT, billing, organization-admin, or API-key management request is exposed.

## Local files

- Input file paths are explicit tool arguments and are validated as existing files.
- `openai_upload_file` requires `confirm_upload=true`; agents must only set it after explicit user authorization because the file is sent to and stored by the OpenAI Platform.
- Audio transcription enforces a 25 MB local upload cap, matching the documented file transcription limit used by this implementation.
- Image edit input and mask each have a 50 MB local cap.
- Generated files are written under `OPENAI_ARTIFACT_DIR`; output names are sanitized to prevent path traversal.

## Costs and retries

- Model calls can incur API charges.
- The server does not automatically retry failed inference requests. This avoids duplicate billable work after ambiguous timeouts.
- A 429 response includes a retry hint when supplied by the API.
- Use `max_output_tokens`, smaller models, and explicit `n` values to control workload size.

## Data handling

- Responses requests default to `store=false`; the caller may explicitly enable storage.
- The server does not persist prompts or responses to a local database.
- Generated artifacts are saved to the configured local directory.
- Do not send sensitive personal data unless the workflow and applicable policies permit it.
