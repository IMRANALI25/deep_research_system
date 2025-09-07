from agents import (
    Agent,
    Runner,
    handoff,
    OpenAIChatCompletionsModel,
    ModelSettings,
    set_tracing_disabled,
    function_tool,
    RunContextWrapper,
    ItemHelpers,
)
from openai import (
    OpenAIError,
    BadRequestError,
    AuthenticationError,
    APIConnectionError,
    APIStatusError,
    APIError,
    AsyncOpenAI,
    RateLimitError,
    PermissionDeniedError,
    NotFoundError,
    InternalServerError,
)
from utilities import (
    api_keys as AK,
    helper_functions as HF,
    llm_parameters as LP,
    config_constants as CC,
    user_profile as UP,
)
from typing import List


def create_orchestrator_agent() -> Agent:
    try:
        # 🎁 Model Settings For Orchestrator Agent
        MODEL_SETTINGS = ModelSettings(
            temperature=1.5,
            top_p=0.75,
        )

        # 🕵🏽 Create Orchestrator Agent
        orchestrator_agent: Agent = Agent(
            name="orchestrator_agent",
            model=LP.LLM_MODEL,
            instructions=CC.ORCHESTRATOR_INSTRUCTIONS,
            tools=[],
            model_settings=MODEL_SETTINGS,
        )
        if orchestrator_agent is None:
            print("🤖 Orchestrator Agent could not be created.")
            exit(1)
        else:
            return orchestrator_agent
    except OpenAIError as e:
        print(f"❌ [OPENAI ERROR] Unexpected client error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ [UNKNOWN ERROR - Orchestrator Agent] {type(e).__name__}: {e}")
        exit(1)
