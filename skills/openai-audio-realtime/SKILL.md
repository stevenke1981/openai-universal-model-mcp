---
name: openai-audio-realtime
description: Use OpenAI Platform audio, transcription, speech, Realtime, and GPT-Live models. Trigger for audio, speech, subtitle, transcription, translation, voice agent, 即時語音, 配音, 語音轉文字, 字幕, or 語音翻譯.
---

# OpenAI Audio and Realtime

## Recorded audio

Use `openai_transcribe_audio` for a completed recording. The default model is `gpt-transcribe`. Select `json`, `text`, `srt`, or `vtt` only when supported by the model. Confirm file format and size before upload.

## Speech generation

Use `openai_generate_speech` only after checking the current `/v1/audio/speech` model support. Legacy TTS model IDs may be deprecated. Save output under the artifact directory and report the exact path.

## Realtime API

1. Call `openai_create_realtime_client_secret` with the chosen Realtime model and session configuration.
2. Pass the short-lived secret to the intended browser/mobile client through a secure channel.
3. The client establishes WebRTC or WebSocket and owns the live audio event loop.
4. Never persist or log the ephemeral secret.

## Realtime translation

Use `openai_create_realtime_translation_secret` for `gpt-realtime-translate`. Pass a session JSON object containing the model and target output language, for example `{"model":"gpt-realtime-translate","audio":{"output":{"language":"ja"}}}`. The client then connects to the Realtime Translation WebSocket and streams audio.

## GPT-Live

1. The client creates an SDP offer.
2. Call `openai_create_live_session` with the SDP offer and session config.
3. Apply the returned SDP answer to the peer connection.
4. The client waits for the session-started event and streams media.

## Boundary

An MCP tool can prepare session setup, but it does not carry a continuous bidirectional audio stream. Do not claim that a live session is fully running just because credentials or an SDP answer were returned.

## Chinese intent

「錄音轉文字」「產生配音」「即時語音對話」「中日口譯」「字幕 SRT/VTT」 are audio workflow triggers.
