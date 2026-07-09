import pytest

from content_agents.graph.workflow import check_news_availability, should_publish
from content_agents.schemas.data_types import Critique, NewsArticle, TweetDraft
from tests.helpers import create_initial_state


@pytest.mark.unit
def test_check_news_routes_to_editor_when_articles_present() -> None:
    article = NewsArticle(
        title="T",
        content="C",
        url="https://example.com",
        source="S",
        published_at="2024-01-01",
    )
    state = create_initial_state(articles=[article])
    assert check_news_availability(state) == "editor"


@pytest.mark.unit
def test_check_news_routes_to_end_when_no_news() -> None:
    state = create_initial_state(topic="None", articles=[])
    assert check_news_availability(state) == "end"


@pytest.mark.unit
def test_check_news_retries_collector() -> None:
    state = create_initial_state(topic="AI", articles=[])
    assert check_news_availability(state) == "collector"


@pytest.mark.unit
def test_should_publish_routes_to_publisher_when_approved() -> None:
    draft = TweetDraft(content="ok", reasoning="r")
    critique = Critique(score=9, feedback="good", is_approved=True)
    state = create_initial_state(draft=draft, critique_history=[critique])
    assert should_publish(state) == "publisher"


@pytest.mark.unit
def test_should_publish_routes_to_end_without_critique_history() -> None:
    assert should_publish(create_initial_state()) == "end"


@pytest.mark.unit
def test_should_publish_routes_to_end_when_no_draft_after_rejection() -> None:
    critique = Critique(score=3, feedback="bad", is_approved=False)
    state = create_initial_state(draft=None, critique_history=[critique])
    assert should_publish(state) == "end"


@pytest.mark.unit
def test_should_publish_routes_to_writer_on_rejection() -> None:
    draft = TweetDraft(content="ok", reasoning="r")
    critique = Critique(score=5, feedback="improve", is_approved=False)
    state = create_initial_state(
        draft=draft,
        critique_history=[critique],
        iteration_count=1,
    )
    assert should_publish(state) == "writer"


@pytest.mark.unit
def test_should_publish_routes_to_end_at_max_iterations() -> None:
    draft = TweetDraft(content="ok", reasoning="r")
    critique = Critique(score=5, feedback="improve", is_approved=False)
    state = create_initial_state(
        draft=draft,
        critique_history=[critique],
        iteration_count=3,
    )
    assert should_publish(state) == "end"
