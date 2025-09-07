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


def create_agent(
    agent_name: str | None,
    model: LP.LLM_MODEL,
    instructions: str | None,
    tools: list | None,
    model_settings: ModelSettings | None,
) -> Agent:
    # 🕵🏽 Create Orchestrator Agent
    try:
        generic_agent: Agent = Agent(
            name=agent_name,
            model=model,
            instructions=instructions,
            tools=[tools],
            model_settings=model_settings,
        )
        return generic_agent
    except OpenAIError as e:
        print(f"❌ [OPENAI ERROR] Unexpected client error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ [UNKNOWN ERROR - Planning Agent] {type(e).__name__}: {e}")
        exit(1)
