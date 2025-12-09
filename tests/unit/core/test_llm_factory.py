from src.content_agents.core.config import settings
from src.content_agents.core.llm import get_llm


def test_llm_factory_configuration() -> None:
    """
    Unit test to ensure the LLM factory picks up settings correctly.
    """
    llm = get_llm()

    assert llm.model_name == settings.model_name
    assert llm.openai_api_base == settings.openai_api_base

    llm_key = llm.openai_api_key
    if hasattr(llm_key, "get_secret_value"):
        llm_key = llm_key.get_secret_value()

    assert llm_key == settings.openai_api_key.get_secret_value()

    assert llm.temperature == 0.7  # noqa: PLR2004


def test_llm_factory_override() -> None:
    """Test that we can override default parameters."""
    custom_temp = 0.1
    llm = get_llm(temperature=custom_temp)

    assert llm.temperature == custom_temp
    assert llm.model_name == settings.model_name
