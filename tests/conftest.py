"""Shared pytest fixtures."""

from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

from content_agents.core.config import settings
from content_agents.services import history as history_module


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

    with patch.object(history_module, "HISTORY_FILE", history_path):
        history_module.history_service.processed_urls = set()
        yield history_path

    history_module.history_service.processed_urls = set()
    history_module.history_service._load()
