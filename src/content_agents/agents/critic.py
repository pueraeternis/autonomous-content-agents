from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.content_agents.core.llm import get_llm
from src.content_agents.core.logger import logger
from src.content_agents.graph.state import AgentState
from src.content_agents.schemas.data_types import Critique

parser = PydanticOutputParser(pydantic_object=Critique)

SYSTEM_PROMPT = """You are a Senior Chief Editor at a top-tier tech news outlet.
Your job is to CRITIQUE the provided tweet draft based on the source articles.

CRITERIA:
1. Factuality: Does the tweet contradict the source articles? (CRITICAL)
2. Value: Is it boring? Does it lack specific details?
3. Style: Is it cringe? (e.g., too many emojis like 🚀🚀🚀, robotic phrasing like "In the ever-evolving landscape").
4. Formatting: Is it readable? 

SCORING:
- 1-5: Reject. Major factual errors or completely boring.
- 6-7: Reject. Needs polish (better hook, less fluff).
- 8-10: Approve. Ready for publication.

OUTPUT FORMAT:
Return a JSON matching the following schema:
{format_instructions}
"""


def critic_node(state: AgentState) -> dict:
    logger.info("Critic Agent reviewing draft...")

    draft = state.get("draft")
    articles = state.get("articles")

    if not draft:
        return {}

    articles_text = "\n\n".join([a.to_markdown() for a in articles])

    content = f"""
    --- SOURCE ARTICLES ---
    {articles_text}
    
    --- PROPOSED TWEET DRAFT ---
    {draft.content}
    
    --- REASONING GIVEN BY WRITER ---
    {draft.reasoning}
    """

    llm = get_llm(temperature=0.0)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(format_instructions=parser.get_format_instructions())),
        HumanMessage(content=content),
    ]

    try:
        response = llm.invoke(messages)
        critique = parser.parse(response.content)

        logger.info("Critique generated", score=critique.score, approved=critique.is_approved)

        return {
            "critique_history": [critique],
        }

    except Exception as e:
        logger.error("Critic failed", error=str(e))
        return {
            "critique_history": [Critique(score=1, feedback="System error during critique.", is_approved=False)],
        }
