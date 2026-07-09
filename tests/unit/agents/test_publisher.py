import pytest

from content_agents.agents.publisher import _smart_truncate


@pytest.mark.unit
def test_smart_truncate_returns_short_content_unchanged() -> None:
    content = "Short text."
    assert _smart_truncate(content, max_length=40) == content


@pytest.mark.unit
def test_smart_truncate_respects_max_length() -> None:
    content = "Hello, world, this is a long sentence without a period at the end"
    result = _smart_truncate(content, max_length=40)
    assert len(result) <= 40


@pytest.mark.unit
def test_smart_truncate_prefers_period_boundary() -> None:
    content = "First sentence. Second sentence that makes this too long."
    result = _smart_truncate(content, max_length=40)
    assert result == "First sentence."
