# Imports
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
    tavily_response_data as TD,
)
from tavily import (
    AsyncTavilyClient,
    MissingAPIKeyError,
    InvalidAPIKeyError,
    UsageLimitExceededError,
    BadRequestError,
)
from research_agents import (
    generic_agent as GA,
    orchestrator_agent as OA,
    solo_agent as SA,
    tavily_client_agent as TA,
    planning_agent as PA,
    web_search_agent as WA,
    synthesizer_agent as SY,
    report_generation_agent as RA,
)

from typing import List, Optional
from pydantic import BaseModel
import os, json, itertools, asyncio, typing
import datetime, time
from dataclasses import dataclass


# 🚀 Initialize Parameters
try:
    # 🔣 LOAD ENVIRONMENT VARIABLES
    AK.get_env_variables()

    # 🔎 Enable/Disable Tracing
    set_tracing_disabled(disabled=True)

    # 🤠INITIALIZE USER OBJECT
    user = HF.get_user_profile()

    # 🧊INITIALIZE CONTEXT OBJECT
    ctx = RunContextWrapper(user)
except Exception as e:
    print(f"❌ [Runner Error] {type(e).__name__}: {e}")
    exit(1)


# 🔑 Load Keys
LP.GEMINI_API_KEY = AK.get_api_key("GEMINI_API_KEY")
LP.TAVILY_API_KEY = AK.get_api_key("TAVILY_API_KEY")

# 👨🏻‍💻 Initialize Tavily Client Object
tavily_client = AsyncTavilyClient(api_key=LP.TAVILY_API_KEY)

def dynamic_instructions(context: RunContextWrapper, agent: Agent) -> str:
    return f"You are {agent.name}. Do deep research according to the user's needs."


# Store original query + all rewritten queries
global last_user_query, tool_call_logs
last_user_query = None

# list of dicts for logging
tool_call_logs = []


@function_tool
async def tavily_deep_search(query: str) -> List[dict]:
    try:
        """Search Tavily with the given query (agent may rewrite it). Verify Query"""
        call_number = len(tool_call_logs) + 1
        log_entry = {
            "call_number": call_number,
            "original_query": last_user_query,
            "rewritten_query": query
        }
        tool_call_logs.append(log_entry)

        print(f"\n🔎 Tool Call #{call_number}")

        print("\n📝 Original user query:", last_user_query)
        print("🤖 Model’s rewritten query:", query)
        # input("Wait for Key Press...")
        # if query is not None:
        #     if query == last_user_query:
        #         query = query
        #     else:
        #         query = last_user_query   
        # elif query != last_user_query:
        #     query = last_user_query
        # else:
        #     query = query

        print("🔎 Now The Final Query :", query)

        raw_response = await tavily_client.search(
            query,
            search_depth="advanced",
            topic="general",
            max_results=2,
            include_raw_content=True,
            include_answer=True,
        )

        # print(f"{raw_response["results"]}")
        # else:
        #     raise ValueError("""\n❌ TAVILY_QUERY Variable is not defined.
        #         Please set the TAVILY_QUERY variable before using this function.
        #         web_search_agent.py - tavily_deep_search()""")
        #     exit(1)
            
        # print("🟠" * 80)
        # print("\n")
        
        response = TD.get_tavily_results(raw_response=raw_response, tavily_client=tavily_client, use_pydantic=True)
        return response
    except MissingAPIKeyError as e:
        print("\n❌ [MISSING API KEY ERROR]:\n", {e})
        exit(1)

    except InvalidAPIKeyError as e:
        print("\n❌ [INVALID API KEY ERROR]:\n", {e})
        exit(1)

    except UsageLimitExceededError as e:
        print("\n❌ [USAGE LIMIT EXCEEDED ERROR]:\n", {e})
        exit(1)

    except BadRequestError as e:
        print("\n❌ [BAD REQUEST ERROR] Invalid parameters", {e})
        exit(1)

    except Exception as e:
        print(f"❌ [ERROR - Web Search Agent.py] {type(e).__name__}: {e}")
        exit(1)



def create_web_search_agent(file_format: HC.FileFormat, research_topic: str) -> Agent:
    
    # Initialize  Variables
    # INSTRUCTIONS = """You are the Expert Web Search Assistant.You always
    #     perform deep research for given topic {research_topic}. 
    #     Always call tavily_deep_search() using the user’s query exactly, 
    #     Do not rewrite or modify the query.
    #     Always use Tavily Web Services for web searching and extract content
    #     from web URLs using content extraction method of tavily for {research_topic} only.
    #     You always discard irrelevant content from tavily output.
    #     You will manage all requirements gathering tasks. 
    #     You must extract content from web URLs using content extraction method 
    #     of tavily web service. You must provide in depth knowledge
    #     and information about the research topic.
    #     """

    INSTRUCTIONS = """You are the Expert Web Search Assistant.You always
        perform deep research using Tavily Web Service. 
        You will manage all requirements gathering tasks. 
        You must extract content from web URLs.
        """
        
    SPECIAL_INSTRUCTIONS_HTML = """ The report must be designed like a 'Responsive WEB Page', 
        Include 'Lazy Loading' with 'animated text and graphics'. 
        Report must use advanced CSS3 rules and HTML5 features.
        Use Colorful Headings and Subheadings of maximum 4 levels deep. 
        Subheadings hierarchy levels should be like this (Heading 1 -> SubHeading LEVEL 1.1 -> SubHeading LEVEL 1.1.1).
        Always create complete CSS3 style and HTML5 document structure in a single output report.
        In Header and Footer of HTML Report Document, always add current System Date and Time. 
        The generated HTML Report must be professionally formatted as a final output. Finally create a professional report in '.html' format."""              

    SPECIAL_INSTRUCTIONS_MD = """The generated MARKDOWN (.md) Report must 
    be professionally formatted as a final output."""

    SPECIAL_INSTRUCTIONS_DOCX = """The generated WORD document (.docx or .doc)
    Report must be professionally formatted as a final output."""

    SPECIAL_INSTRUCTIONS_PDF = """The generated PDF document (.pdf) Report must 
    be professionally formatted as a final output."""

    SPECIAL_INSTRUCTIONS_JSON = """The generated JSON (.json) Report must 
    be professionally structured as a final output."""

    SPECIAL_INSTRUCTIONS_CSV = """The generated Comma Separated Values (.csv)
    Report must be professionally formatted as a final output."""

    SPECIAL_INSTRUCTIONS_XML = """The generated XML Extensible MArkup Language
    (.xml) Report must be professionally formatted as a final output."""

    SPECIAL_INSTRUCTIONS_TXT = """The generated TEXT File (.txt) Report must 
    be professionally formatted as a final output."""

    last_user_query = {research_topic}
    # print(last_user_query)

    try:
        # 🎁 Model Settings For Web Search Agent
        MODEL_SETTINGS = ModelSettings(
            temperature=1.5,
            top_p=0.75,
            tool_choice="required",
        )

        if file_format.value == "HTML":
            SPECIAL_INSTRUCTIONS = SPECIAL_INSTRUCTIONS_HTML
        elif file_format.value == "MD":
            SPECIAL_INSTRUCTIONS = SPECIAL_INSTRUCTIONS_MD
        elif file_format.value == "DOCX":
            SPECIAL_INSTRUCTIONS = SPECIAL_INSTRUCTIONS_DOCX
        elif file_format.value == "PDF":
            SPECIAL_INSTRUCTIONS = SPECIAL_INSTRUCTIONS_PDF
        elif file_format.value == "JSON":
            SPECIAL_INSTRUCTIONS = SPECIAL_INSTRUCTIONS_JSON
        elif file_format.value == "CSV":
            SPECIAL_INSTRUCTIONS = SPECIAL_INSTRUCTIONS_CSV
        elif file_format.value == "XML":
            SPECIAL_INSTRUCTIONS = SPECIAL_INSTRUCTIONS_XML
        elif file_format.value == "TXT":
            SPECIAL_INSTRUCTIONS = SPECIAL_INSTRUCTIONS_TXT

        # 🕵🏽 Create Tavily Client Agent
        web_search_agent: Agent = Agent(
            name="web_search_agent",
            model=LP.LLM_MODEL,
            instructions=f"{INSTRUCTIONS}\n\n{SPECIAL_INSTRUCTIONS}",
            tools=[tavily_deep_search],
            model_settings=MODEL_SETTINGS,
        )
        if web_search_agent is None:
            print("🤖 Tavily Client Agent could not be created.")
            exit(1)
        else:
            return web_search_agent
    except OpenAIError as e:
        print(f"❌ [OPENAI ERROR] Unexpected client error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ [ERROR - Web Search Agent - create_web_search_agent()] {type(e).__name__}: {e}")
        exit(1)
