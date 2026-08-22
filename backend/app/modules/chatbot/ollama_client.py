import httpx
import json
from typing import AsyncIterator
from app.core.config import settings
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))

async def stream_completion(messages: list[dict]) -> AsyncIterator[str]:
    """
    messages: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    Yields string chunks as they arrive from Ollama.
    """
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": True}
    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/chat", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    if content := chunk.get("message", {}).get("content"):
                        yield content
                    if chunk.get("done"):
                        break

async def check_ollama_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return r.status_code == 200
    except Exception:
        return False
