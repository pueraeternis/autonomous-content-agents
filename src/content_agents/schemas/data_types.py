from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """Structure of a raw news article obtained from RSS or an API."""

    title: str
    content: str
    url: str
    source: str
    published_at: str
    image_url: str | None = None

    def to_markdown(self) -> str:
        """Format the prompt."""
        md = f"# {self.title}\n\nSource: {self.source}\nLink: {self.url}\n\n{self.content}"
        if self.image_url:
            md += f"\n\n![Image]({self.image_url})"
        return md


class TweetDraft(BaseModel):
    """Draft of a tweet (or thread)."""

    content: str = Field(..., description="Tweet text (up to 280 characters or a thread)")
    media_files: list[str] = Field(default_factory=list, description="Paths to images or base64 strings")
    reasoning: str = Field(..., description="Explanation of the chosen style and tone")


class Critique(BaseModel):
    """Content quality evaluation."""

    score: int = Field(..., ge=1, le=10, description="Rating from 1 to 10")
    feedback: str = Field(..., description="What to improve")
    is_approved: bool = Field(..., description="Is the content allowed to be published?")
