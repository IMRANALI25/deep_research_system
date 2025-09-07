# create_tavily_client_agent
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
    helper_classes as HC,
)
from typing import List
from research_agents import planning_agent as PA
def dynamic_instructions(context: RunContextWrapper, agent: Agent) -> str:
    return f"You are {agent.name}. Do deep research according to the user's needs."


def create_requirement_agent(file_format: HC.FileFormat, research_topic: str) -> Agent:
    # Initialize  Variables
    INSTRUCTIONS = """You are the Expert Deep Research requirement Assistant.
        Always gather requirements for the given topic {research_topic}. 
        Always use the user’s query exactly, without rewriting it.
        Never include irrelevant content from web search output. 
        You will manage all requirement gathering tasks.
        Send all requirements to the Planning agent.
        Always Handoffs to the Planning Agent."""

    SPECIAL_INSTRUCTIONS = """Always send deep research rquirements to the 
    planning agent.Always Handoffs to the Planning Agent."""

    try:
        planning_agent = PA.create_planning_agent(file_format, research_topic)
        
        # 🎁 Model Settings For Orchestrator Agent
        MODEL_SETTINGS = ModelSettings(
            temperature=1.3,
            top_p=0.85,
        )

        # 🕵🏽 Create requirement Agent
        requirement_agent: Agent = Agent(
            name="requirement_agent",
            model=LP.LLM_MODEL,
            instructions=f"{INSTRUCTIONS}\n\n{SPECIAL_INSTRUCTIONS}",
            model_settings=MODEL_SETTINGS,
            handoffs=[planning_agent]
        )
        if requirement_agent is None:
            print("🤖 Requirement Agent could not be created.")
            exit(1)
        else:
            return requirement_agent
    except OpenAIError as e:
        print(f"❌ [OPENAI ERROR] Unexpected client error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ [ERROR - requirement Agent - create_requirement_agent()] {type(e).__name__}: {e}")
        exit(1)
