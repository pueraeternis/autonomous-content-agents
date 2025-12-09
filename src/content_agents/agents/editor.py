from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from src.content_agents.core.llm import get_llm
from src.content_agents.core.logger import logger
from src.content_agents.graph.state import AgentState


class EditorSelection(BaseModel):
    index: int = Field(..., description="Index of the best article (0-based)")
    reasoning: str = Field(..., description="Why this is the most impactful story")


parser = PydanticOutputParser(pydantic_object=EditorSelection)

SYSTEM_PROMPT = """You are a Lead Editor for an AI News Channel.
You have a list of potential news stories.

YOUR TASK:
Select the SINGLE most important, viral, or technically significant story to publish right now.
Ignore fluff, marketing, or minor updates. Look for breakthroughs, major releases, or drama.

OUTPUT FORMAT:
Return a JSON with the 'index' of the selected article and your 'reasoning'.
{format_instructions}
"""


def editor_node(state: AgentState) -> dict:
    logger.info("Editor Agent selecting the best story...")

    articles = state.get("articles", [])
    if not articles:
        return {}

    titles_text = "\n".join([f"{i}. {a.title} (Source: {a.source})" for i, a in enumerate(articles)])

    llm = get_llm(temperature=0.1)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(format_instructions=parser.get_format_instructions())),
        HumanMessage(content=f"Here are the candidate stories:\n\n{titles_text}"),
    ]

    try:
        response = llm.invoke(messages)
        selection = parser.parse(response.content)

        idx = selection.index
        if 0 <= idx < len(articles):
            selected = articles[idx]
            logger.info("Editor selected story", title=selected.title, reason=selection.reasoning)
            return {"selected_article": selected}
        logger.error("Editor returned invalid index", index=idx, max_index=len(articles) - 1)
        return {"selected_article": articles[0]}

    except Exception as e:
        logger.error("Editor failed selection", error=str(e))
        return {"selected_article": articles[0]}
