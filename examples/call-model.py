"""Small direct REST example; set OPENAI_API_KEY before running."""
import os

import httpx


def main() -> None:
    key = os.environ["OPENAI_API_KEY"]
    response = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": "gpt-6.1-sol",
            "input": "Explain MCP in three concise bullet points.",
            "store": False,
        },
        timeout=180,
    )
    response.raise_for_status()
    payload = response.json()
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                print(content.get("text", ""))


if __name__ == "__main__":
    main()
