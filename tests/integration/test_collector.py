from typing import TYPE_CHECKING

import pytest

from src.content_agents.agents.collector import collector_node

if TYPE_CHECKING:
    from src.content_agents.graph.state import AgentState


def test_collector_node_real_fetch() -> None:
    """
    Integration test: Runs the collector node and checks if it fetches real data.
    Requires internet connection.
    """
    # Mock initial state
    initial_state: AgentState = {
        "topic": "",
        "articles": [],
        "draft": None,
        "critique_history": [],
        "iteration_count": 0,
        "final_tweet_id": None,
    }

    # Run the node
    update = collector_node(initial_state)

    # Check results
    assert "topic" in update
    assert update["topic"] != ""
    assert isinstance(update["articles"], list)

    # Warning: This might fail if no news in last 24h, but usually Major AI sources have something.
    if len(update["articles"]) > 0:
        print(f"\n✅ Fetched {len(update['articles'])} articles for topic: {update['topic']}")
        print(f"Sample title: {update['articles'][0].title}")
        print(f"Sample Image URL: {update['articles'][0].image_url}")
    else:
        pytest.skip("No fresh news found in the last 24h (check sources.json)")
