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
from research_agents import lead_research_agent as LA
def dynamic_instructions(context: RunContextWrapper, agent: Agent) -> str:
    return f"You are {agent.name}. Do deep research according to the user's needs."

def on_handoff(agent: Agent, ctx: RunContextWrapper):
    print("🔵" * 50)
    print(f"🔀 Handing off to 🕵️‍♂️  {agent.name}...")
    print("🔵" * 50)
    print("Transferring to the Lead Agent, input_data:")
    return ctx

def create_planning_agent(file_format: HC.FileFormat, research_topic: str) -> Agent:
    # Initialize  Variables
    INSTRUCTIONS = """You are the Expert Deep Research Planning Assistant.
        Get requirements from the agent and plan a deep research report.
        You always plan summarized query for the given topic {research_topic}. 
        Always use the user’s query exactly, without rewriting it.
        Never include irrelevant content from web search output. 
        You will manage all planning tasks and create summarized query 
        for deep research and send this summarized query to the Lead Research agent.
        Always Handoffs to the Lead Research Agent."""

    SPECIAL_INSTRUCTIONS = """Always send deep research summarized query to the 
    Lead Research agent.Always Handoffs to the Lead Research Agent."""

    try:
        lead_research_agent = LA.create_lead_research_agent(file_format, research_topic)

        # 🎁 Model Settings For Orchestrator Agent
        MODEL_SETTINGS = ModelSettings(
            temperature=1.2,
            top_p=0.85,
        )

        # 🕵🏽 Create planning Agent
        planning_agent: Agent = Agent(
            name="planning_agent",
            model=LP.LLM_MODEL,
            instructions=f"{INSTRUCTIONS}\n\n{SPECIAL_INSTRUCTIONS}",
            model_settings=MODEL_SETTINGS,
            handoffs=[lead_research_agent]
        )
        if planning_agent is None:
            print("🤖 planning Agent could not be created.")
            exit(1)
        else:
            return planning_agent
    except OpenAIError as e:
        print(f"❌ [OPENAI ERROR] Unexpected client error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ [ERROR - planning Agent - create_planning_agent()] {type(e).__name__}: {e}")
        exit(1)
