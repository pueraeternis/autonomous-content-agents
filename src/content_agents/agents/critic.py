from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from content_agents.core.config import settings
from content_agents.core.llm import get_llm
from content_agents.core.logger import logger
from content_agents.graph.constants import MAX_ITERATIONS
from content_agents.graph.state import AgentState
from content_agents.schemas.data_types import Critique

parser = PydanticOutputParser(pydantic_object=Critique)

SYSTEM_PROMPT = f"""You are a Senior Chief Editor at a top-tier tech news outlet.
Your job is to CRITIQUE the provided tweet draft based on the source articles.

CRITERIA:
1. Length: Is it strictly under {settings.twitter_max_length} characters? (CRITICAL - Reject immediately if longer).
2. Factuality: Does the tweet contradict the source articles?
3. Value: Is it boring? Does it lack specific details?

SCORING:
- 1-5: Reject. Factual errors or OVER {settings.twitter_max_length} CHARACTERS.
- 6-7: Reject. Needs polish.
- 8-10: Approve. Ready for publication.

OUTPUT FORMAT:
Return a JSON matching the following schema:
{{format_instructions}}
"""


def critic_node(state: AgentState) -> dict[str, Any]:
    """
    Critic Agent:
    1. Checks hard constraints (Length).
    2. Reviews the current draft using LLM.
    """
    logger.info("Critic Agent reviewing draft...")

    draft = state.get("draft")
    if not draft:
        return {
            "critique_history": [
                Critique(
                    score=1,
                    is_approved=False,
                    feedback="No draft available for review.",
                ),
            ],
            "termination_reason": "writer_failed",
        }

    # --- HARD CONSTRAINT CHECK (Python side) ---
    if len(draft.content) > settings.twitter_max_length:
        logger.warning(
            "Draft is too long, rejecting automatically.", length=len(draft.content)
        )
        critique = Critique(
            score=2,
            is_approved=False,
            feedback=(
                f"Too long! The draft is {len(draft.content)} characters, "
                f"but the limit is {settings.twitter_max_length}. Shorten it significantly."
            ),
        )
        return _build_critique_response(state, critique)

    # --- LLM Semantic Review ---
    articles = state.get("articles")
    articles_text = "\n\n".join([a.to_markdown() for a in articles])

    prompt = f"""
    --- SOURCE ARTICLES ---
    {articles_text}

    --- PROPOSED TWEET DRAFT ---
    {draft.content}

    --- REASONING GIVEN BY WRITER ---
    {draft.reasoning}
    """

    llm = get_llm(temperature=0.0, role="critic")

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT.format(
                format_instructions=parser.get_format_instructions()
            )
        ),
        HumanMessage(content=prompt),
    ]

    try:
        response = llm.invoke(messages)
        response_text = response.content
        if not isinstance(response_text, str):
            raise TypeError("Expected string content from LLM response")
        critique = parser.parse(response_text)

        logger.info(
            "Critique generated", score=critique.score, approved=critique.is_approved
        )

        return _build_critique_response(state, critique)

    except Exception as e:
        logger.error("Critic failed", error=str(e))
        return _build_critique_response(
            state,
            Critique(
                score=1, feedback="System error during critique.", is_approved=False
            ),
        )


def _build_critique_response(state: AgentState, critique: Critique) -> dict[str, Any]:
    result: dict[str, Any] = {"critique_history": [critique]}

    if not critique.is_approved and state.get("iteration_count", 0) >= MAX_ITERATIONS:
        result["termination_reason"] = "max_iterations"

    return result
