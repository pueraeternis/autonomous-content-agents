import operator
from typing import Annotated, TypedDict

from src.content_agents.schemas.data_types import Critique, NewsArticle, TweetDraft


class AgentState(TypedDict):
    """
    Global state of the graph.
    """

    tried_rubrics: Annotated[list[str], operator.add]
    topic: str
    articles: list[NewsArticle]
    selected_article: NewsArticle | None
    draft: TweetDraft | None
    critique_history: Annotated[list[Critique], operator.add]
    iteration_count: int
    final_tweet_id: str | None
