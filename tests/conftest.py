"""Shared pytest fixtures."""

from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path

import pytest
import requests

from content_agents.core.config import settings
from content_agents.services.history import history_service


@pytest.fixture
def twitter_credentials_available() -> bool:
    return bool(
        settings.twitter_api_key
        and settings.twitter_api_secret
        and settings.twitter_access_token
        and settings.twitter_access_secret
    )


@pytest.fixture
def vllm_available() -> bool:
    health_url = settings.openai_api_base.rstrip("/") + "/models"
    try:
        response = requests.get(health_url, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


@pytest.fixture
def tmp_history_file(tmp_path: Path) -> Generator[Path, None, None]:
    history_path = tmp_path / "history.json"
    history_path.write_text(json.dumps({"urls": []}), encoding="utf-8")

    original_file = history_service.history_file
    history_service.use_file(history_path)
    yield history_path
    history_service.use_file(original_file)
