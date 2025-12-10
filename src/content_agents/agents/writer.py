from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.content_agents.core.config import settings
from src.content_agents.core.llm import get_llm
from src.content_agents.core.logger import logger
from src.content_agents.core.utils import download_image_as_base64
from src.content_agents.graph.state import AgentState
from src.content_agents.schemas.data_types import TweetDraft

parser = PydanticOutputParser(pydantic_object=TweetDraft)

SYSTEM_PROMPT = f"""You are a Senior Tech Journalist writing for X (Twitter).

YOUR TASK:
Write a viral, engaging tweet about the provided news article.

GUIDELINES:
1. Hook: Start with a strong insight or breaking news alert.
2. Value: Explain the impact for AI engineers.
3. Tone: Professional, concise, no marketing fluff.
4. Constraints: EXTREMELY SHORT. Max {settings.writer_target_length} characters. NO Threads.

OUTPUT FORMAT:
{{format_instructions}}
"""


def writer_node(state: AgentState) -> dict:
    logger.info("Writer Agent starting...")

    current_iter = state.get("iteration_count", 0)
    new_iter = current_iter
    if state.get("critique_history"):
        new_iter += 1

    article = state.get("selected_article")

    if not article:
        logger.error("Writer received no selected article!")
        return {"draft": None}

    content_blocks = []

    content_blocks.append(
        {
            "type": "text",
            "text": f"SOURCE MATERIAL:\n{article.to_markdown()}",
        },
    )

    image_attached = False
    if article.image_url:
        b64_img = download_image_as_base64(article.image_url)
        if b64_img:
            content_blocks.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"},
                },
            )
            image_attached = True
            logger.info("Attached image to prompt", url=article.image_url)

    # Feedback Loop
    critique_history = state.get("critique_history", [])
    if critique_history:
        last_critique = critique_history[-1]
        previous_draft = state.get("draft")

        logger.info("Writer received feedback", feedback=last_critique.feedback)

        if "Too long" in last_critique.feedback:
            instruction = "CRITICAL: The text is too long. REMOVE all adjectives. REMOVE hashtags if needed. Make it 50% shorter."
        else:
            instruction = "Rewrite the tweet to address this feedback explicitly."

        feedback_prompt = f"""
        ⚠️ IMPORTANT: FEEDBACK ON PREVIOUS VERSION
        Your previous draft was REJECTED with score {last_critique.score}/10.
        
        PREVIOUS DRAFT ({len(previous_draft.content) if previous_draft else 0} chars):
        {previous_draft.content if previous_draft else "N/A"}
        
        EDITOR FEEDBACK:
        "{last_critique.feedback}"
        
        INSTRUCTION:
        {instruction}
        Target length: < {settings.writer_target_length} characters.
        """

        content_blocks.append(
            {
                "type": "text",
                "text": feedback_prompt,
            },
        )

    llm = get_llm(temperature=0.7)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(format_instructions=parser.get_format_instructions())),
        HumanMessage(content=content_blocks),
    ]

    try:
        response = llm.invoke(messages)
        draft = parser.parse(response.content)

        if image_attached:
            draft.media_files = [article.image_url]
        else:
            draft.media_files = []

        logger.info("Draft generated successfully", content_snippet=draft.content[:50], length=len(draft.content))

        return {
            "draft": draft,
            "iteration_count": new_iter,
        }

    except Exception as e:
        logger.error("Writer failed to generate draft", error=str(e))
        return {"draft": None}
