import operator
from typing import Annotated, Literal, TypedDict

from content_agents.schemas.data_types import Critique, NewsArticle, TweetDraft


class AgentState(TypedDict):
    """Global state of the graph."""

    tried_rubrics: Annotated[list[str], operator.add]
    topic: str
    articles: list[NewsArticle]
    selected_article: NewsArticle | None
    draft: TweetDraft | None
    critique_history: Annotated[list[Critique], operator.add]
    iteration_count: int
    final_tweet_id: str | None
    termination_reason: str | None
    publish_mode: Literal["live", "mock"] | None


def create_initial_state() -> AgentState:
    return {
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
