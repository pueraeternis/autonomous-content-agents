from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.content_agents.core.llm import get_llm
from src.content_agents.core.logger import logger
from src.content_agents.graph.state import AgentState
from src.content_agents.schemas.data_types import Critique

parser = PydanticOutputParser(pydantic_object=Critique)

MAX_POST_LENGTH = 280

SYSTEM_PROMPT = """You are a Senior Chief Editor at a top-tier tech news outlet.
Your job is to CRITIQUE the provided tweet draft based on the source articles.

CRITERIA:
1. Length: Is it strictly under 280 characters? (CRITICAL - Reject immediately if longer).
2. Factuality: Does the tweet contradict the source articles?
3. Value: Is it boring? Does it lack specific details?
4. Style: Is it cringe? (Too many emojis, robotic phrasing).

SCORING:
- 1-5: Reject. Factual errors or OVER 280 CHARACTERS.
- 6-7: Reject. Needs polish (better hook, make it shorter).
- 8-10: Approve. Ready for publication.

OUTPUT FORMAT:
Return a JSON matching the following schema:
{format_instructions}
"""


def critic_node(state: AgentState) -> dict:
    """
    Critic Agent:
    1. Checks hard constraints (Length).
    2. Reviews the current draft using LLM.
    """
    logger.info("Critic Agent reviewing draft...")

    draft = state.get("draft")
    if not draft:
        return {}

    # --- HARD CONSTRAINT CHECK (Python side) ---
    if len(draft.content) > MAX_POST_LENGTH:
        logger.warning("Draft is too long, rejecting automatically.", length=len(draft.content))
        return {
            "critique_history": [
                Critique(
                    score=2,
                    is_approved=False,
                    feedback=f"Too long! The draft is {len(draft.content)} characters, but the limit is 280. Shorten it significantly.",
                ),
            ],
        }

    # --- LLM Semantic Review ---
    articles = state.get("articles")
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
