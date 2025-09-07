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

def dynamic_instructions(context: RunContextWrapper, agent: Agent) -> str:
    return f"You are {agent.name}. Do deep research according to the user's needs."

def on_handoff(agent: Agent, ctx: RunContextWrapper):
    print("🔵" * 50)
    print(f"🔀 Handing off to 🕵️‍♂️  {agent.name}...")
    print("🔵" * 50)
    print("Transferring to the Lead Agent, input_data:")
    return ctx

def create_synthesizer_agent(file_format: HC.FileFormat, research_topic: str) -> Agent:
    # Initialize  Variables
    INSTRUCTIONS = """You are the Expert Deep Research Synthesizer Assistant.
        Get requirements from the Lead Research Agent and plan a deep research report.
        Never include irrelevant content from web search output.
        You are responsible for integrating information collected from multiple 
        research processes into a unified, structured, and high-quality output.
        You ensures that findings are not only accurate but also concise, 
        logically organized, and aligned with the original research requirements.
        You are Responsible for:
        1.	Aggregation of Results
        2.	Cross-Validation & Consistency Check
        3.	Advanced Summarization & Abstraction
        4.	Traceability & Transparency
        5.	Relevance Filtering
        """

    SPECIAL_INSTRUCTIONS = """You must complete Deliverable Preparation,
        synthesized report or structured dataset.
        Then send your result to Report Generation Agent.
        Always Handoffs to the Report Generation Agent."""

    try:
        # 🎁 Model Settings For Orchestrator Agent
        MODEL_SETTINGS = ModelSettings(
            temperature=1.3,
            top_p=0.85,
        )

        # 🕵🏽 Create synthesizer Agent
        synthesizer_agent: Agent = Agent(
            name="synthesizer_agent",
            model=LP.LLM_MODEL,
            instructions=f"{INSTRUCTIONS}\n\n{SPECIAL_INSTRUCTIONS}",
            model_settings=MODEL_SETTINGS,
        )
        if synthesizer_agent is None:
            print("🤖 synthesizer Agent could not be created.")
            exit(1)
        else:
            return synthesizer_agent
    except OpenAIError as e:
        print(f"❌ [OPENAI ERROR] Unexpected client error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ [ERROR - synthesizer Agent - create_synthesizer_agent()] {type(e).__name__}: {e}")
        exit(1)
