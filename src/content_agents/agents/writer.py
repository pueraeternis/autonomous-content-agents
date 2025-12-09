from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.content_agents.core.llm import get_llm
from src.content_agents.core.logger import logger
from src.content_agents.core.utils import download_image_as_base64
from src.content_agents.graph.state import AgentState
from src.content_agents.schemas.data_types import TweetDraft

parser = PydanticOutputParser(pydantic_object=TweetDraft)

SYSTEM_PROMPT = """You are a Senior Tech Journalist writing for X (Twitter).
Your goal is to write a viral, engaging, and factual tweet (or thread) based on the provided news articles.

GUIDELINES:
1. Hook: Start with a strong, attention-grabbing first line.
2. Value: Explain WHY this matters to the AI engineer or tech enthusiast.
3. Tone: Professional yet conversational. Avoid marketing fluff ("revolutionary", "game-changing"). Be specific.
4. Format: Use short paragraphs. Use bullet points if listing features. Use appropriate emojis (limit to 2-3).
5. Media: If images are provided in the context, analyze them to add descriptive details to your tweet.
6. Length: If the content is long, write a thread (max 3 tweets connected).

OUTPUT FORMAT:
You MUST return a JSON object matching the following schema:
{format_instructions}
"""


def writer_node(state: AgentState) -> dict:
    logger.info("Writer Agent starting...", topic=state["topic"])

    current_iter = state.get("iteration_count", 0)
    new_iter = current_iter

    if state.get("critique_history"):
        new_iter += 1

    articles = state["articles"]
    if not articles:
        logger.warning("No articles to write about.")
        return {"draft": None}

    content_blocks = []
    articles_text = "\n\n".join([a.to_markdown() for a in articles])
    content_blocks.append(
        {
            "type": "text",
            "text": f"TOPIC: {state['topic']}\n\nSOURCE MATERIALS:\n{articles_text}",
        },
    )

    image_attached = False
    for article in articles:
        if article.image_url and not image_attached:
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

    critique_history = state.get("critique_history", [])
    if critique_history:
        last_critique = critique_history[-1]
        previous_draft = state.get("draft")

        logger.info("Writer received feedback", feedback=last_critique.feedback)

        feedback_prompt = f"""
        ⚠️ IMPORTANT: FEEDBACK ON PREVIOUS VERSION
        Your previous draft was REJECTED with score {last_critique.score}/10.
        
        PREVIOUS DRAFT:
        {previous_draft.content if previous_draft else "N/A"}
        
        EDITOR FEEDBACK:
        "{last_critique.feedback}"
        
        INSTRUCTION:
        Rewrite the tweet to address this feedback explicitly. Improve it.
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
            for art in articles:
                if art.image_url:
                    draft.media_files.append(art.image_url)
                    break

        logger.info("Draft generated successfully")
        draft.media_files = list(set(draft.media_files))
        return {
            "draft": draft,
            "iteration_count": new_iter,
        }

    except Exception as e:
        logger.error("Writer failed to generate draft", error=str(e))
        return {"draft": None}
