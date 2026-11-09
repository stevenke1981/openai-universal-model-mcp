---
name: openai-embeddings-safety
description: Create OpenAI text embeddings and classify potentially harmful text or images. Trigger for embeddings, vector search, semantic search, moderation, safety classification, 向量化, 語意搜尋, 內容審查, or 安全分類.
---

# Embeddings and Moderation

## Embeddings

- Use `openai_create_embeddings` with a documented embedding model.
- `text-embedding-3-large` favors capability; `text-embedding-3-small` favors efficiency.
- Use `dimensions` only when supported by the chosen model.
- Keep `include_vectors=false` unless the vector values are needed by the next step.
- For vector search, store vectors with source IDs and use cosine similarity or a vector database.

## Moderation

- Use `openai_moderate_content` for supported text and image inputs.
- Start with the `flagged` field, then inspect categories and scores.
- Treat scores as signals for a human/application policy, not an automatic universal blocking rule.
- Do not send known or suspected CSAM to the Moderation API; follow OpenAI child-safety guidance.

## Chinese intent

「向量資料」「RAG」「語意檢索」「檢查內容安全」「圖片安全審核」 are triggers.
