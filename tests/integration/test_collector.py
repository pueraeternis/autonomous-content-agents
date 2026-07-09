from typing import TYPE_CHECKING

import pytest

from content_agents.agents.collector import collector_node

if TYPE_CHECKING:
    from content_agents.graph.state import AgentState


@pytest.mark.integration
@pytest.mark.network
def test_collector_node_real_fetch() -> None:
    """
    Integration test: Runs the collector node and checks if it fetches real data.
    Requires internet connection.
    """
    initial_state: AgentState = {
        "topic": "",
        "articles": [],
        "draft": None,
        "critique_history": [],
        "iteration_count": 0,
        "final_tweet_id": None,
        "tried_rubrics": [],
        "selected_article": None,
        "termination_reason": None,
        "publish_mode": None,
    }

    update = collector_node(initial_state)

    assert "topic" in update
    assert update["topic"] != ""
    assert isinstance(update["articles"], list)

    if len(update["articles"]) > 0:
        print(
            f"\nFetched {len(update['articles'])} articles for topic: {update['topic']}"
        )
        print(f"Sample title: {update['articles'][0].title}")
        print(f"Sample Image URL: {update['articles'][0].image_url}")
    else:
        pytest.skip("No fresh news found in the last 24h (check sources.json)")
