import base64
import os

import pytest
import requests
from openai import OpenAI

VLLM_BASE_URL = os.getenv("OPENAI_API_BASE", "http://localhost:8000/v1")
VLLM_API_KEY = os.getenv("OPENAI_API_KEY", "local-dev-key")
MODEL_NAME = "google/gemma-3-27b-it"


@pytest.fixture(scope="module")
def llm_client() -> OpenAI:
    return OpenAI(base_url=VLLM_BASE_URL, api_key=VLLM_API_KEY)


def encode_image_base64(url: str) -> str:
    """Download image and convert to base64."""
    headers = {
        "User-Agent": "Mozilla/5.0 (IntegrationTest/1.0)",
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return base64.b64encode(response.content).decode("utf-8")


@pytest.mark.asyncio
async def test_gemma_vision_capabilities(llm_client: OpenAI) -> None:
    """
    Smoke test. We check that the model can see the cat.
    """
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1024px-Cat03.jpg"
    try:
        base64_image = encode_image_base64(image_url)
    except Exception as e:
        pytest.skip(f"Failed to download test image: {e}")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What animal is in this image? Answer in one word."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        },
    ]

    response = llm_client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=20,
    )

    content = response.choices[0].message.content.lower().strip()
    print(f"\nModel output: {content}")

    assert content, "Model returned empty response"
    assert "cat" in content or "feline" in content, f"Model failed to identify a cat. Got: {content}"
