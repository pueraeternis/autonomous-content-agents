import base64

import requests

from src.content_agents.core.logger import logger


def download_image_as_base64(url: str, timeout: int = 10) -> str | None:
    """
    Download an image from a URL and converts it to a base64 string.
    Returns None if download fails (so the agent can continue with text only).
    """
    if not url:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            logger.warning("URL is not an image", url=url, content_type=content_type)
            return None

        return base64.b64encode(response.content).decode("utf-8")

    except Exception as e:
        logger.warning("Failed to download image", url=url, error=str(e))
        return None
