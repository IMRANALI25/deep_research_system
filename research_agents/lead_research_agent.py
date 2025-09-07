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
from research_agents import (
    generic_agent as GA,
    orchestrator_agent as OA,
    solo_agent as SA,
    tavily_client_agent as TA,
)
from research_agents import web_search_agent as WA
from research_agents import synthesizer_agent as SY
from research_agents import report_generation_agent as RA


def dynamic_instructions(context: RunContextWrapper, agent: Agent) -> str:
    return f"You are {agent.name}. Do deep research according to the user's needs."


# Initialize child agents
# response_web = None
# response_syn = None
# response_rep = None

# web_search_agent = WA.create_web_search_agent()
# synthesizer_agent = SY.create_synthesizer_agent()
# report_generation_agent = RA.create_report_generation_agent()

# @function_tool
# async def web_search_agent_tool(research_topic: str) -> List[dict]:
#     response = await web_search_agent.run(research_topic)
#     return response.get("results")

# @function_tool
# async def synthesizer_agent_tool(data: List[dict]) -> List[dict]:
#     response = await synthesizer_agent.run(data)
#     return response

# @function_tool
# async def report_generation_agent_tool(data: List[dict]) -> List[dict]:
#     response = await report_generation_agent.run(data)
#     return response

def create_lead_research_agent(file_format: HC.FileFormat, research_topic: str) -> Agent:
    # Initialize  Variables
    INSTRUCTIONS = """You are the Expert Deep Research Assistant. 
    You orchestrate all deep research tasks with the help of agent tools.
    Get Summarized Query from Planning Agent and send it to the web search agent.
    Then you will use tavily web search service to collect best and related informative data about {research_topic}.
    After that, you will use Synthesizer Agent to take all research findings and organize them into clear sections with themes, trends, and key insights.
    Finally, you will use Report Generation Agent to generate a professionally documented research report.
    You will use these agents as tools:
    - Web Research Agent (web_research_agent)
    - Synthesizer Agent (synthesizer_agent)
    - Report Generation Agent (report_generation_agent)"""

    SPECIAL_INSTRUCTIONS = """You must strictly follow this sequence of actions:
    1. Web Search Agent (web_search_agent)
    2. Synthesizer Agent (synthesizer_agent)
    3. Report Generation Agent (report_generation_agent)"""

    try:
        # 🎁 Model Settings For Orchestrator Agent
        MODEL_SETTINGS = ModelSettings(
            temperature=0.5,
            top_p=0.80,
            tool_choice="required"
        )

        web_search_agent = WA.create_web_search_agent(HC.FileFormat.MD, CC.RESEARCH_TOPIC)
        synthesizer_agent = SY.create_synthesizer_agent(HC.FileFormat.MD, CC.RESEARCH_TOPIC)
        report_generation_agent = RA.create_report_generation_agent(HC.FileFormat.MD, CC.RESEARCH_TOPIC)    
        
        # 🕵🏽 Create lead_research Agent
        lead_research_agent: Agent = Agent(
            name="lead_research_agent",
            model=LP.LLM_MODEL,
            instructions=f"{INSTRUCTIONS}\n\n{SPECIAL_INSTRUCTIONS}",
            model_settings=MODEL_SETTINGS,
            tools=[
                    web_search_agent.as_tool(tool_name="Web_search_agent",
                    tool_description="Search from the web using Tavily Web Search Service.",
                    ),
                    synthesizer_agent.as_tool(
                    tool_name="synthesizer_agent",
                    tool_description="Synthesize all research data for final reporting"),
                    report_generation_agent.as_tool(
                    tool_name="report_generation_agent",
                    tool_description="Produce final professional report"),
                ],
        )
        if lead_research_agent is None:
            print("🤖 Lead Research Agent could not be created.")
            exit(1)
        else:
            return lead_research_agent
    except OpenAIError as e:
        print(f"❌ [OPENAI ERROR] Unexpected client error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ [ERROR - Lead Research Agent - create_lead_research_agent()] {type(e).__name__}: {e}")
        exit(1)
