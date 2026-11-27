"""OpenAI-backed chat service using the current asynchronous SDK."""
import os

from openai import AsyncOpenAI


async def query_llm(message: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("The AI provider is not configured.")

    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=os.getenv("KUBUVERSE_OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "You're a helpful project assistant."},
            {"role": "user", "content": message},
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    return (response.choices[0].message.content or "").strip()
