from src.content_agents.schemas.data_types import NewsArticle


def test_article_markdown() -> None:
    art = NewsArticle(
        title="AI News",
        content="Gemma 3 released.",
        url="http://google.com",
        source="Google",
        published_at="2025-12-09",
    )
    md = art.to_markdown()
    assert "# AI News" in md
    assert "Gemma 3 released." in md
