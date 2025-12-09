import operator
from typing import Annotated, TypedDict

from src.content_agents.schemas.data_types import Critique, NewsArticle, TweetDraft


class AgentState(TypedDict):
    """
    Global state of the graph.
    LangGraph uses reducers (e.g., operator.add) to merge history.
    """

    topic: str
    articles: list[NewsArticle]

    draft: TweetDraft | None

    critique_history: Annotated[list[Critique], operator.add]

    iteration_count: int
    final_tweet_id: str | None
