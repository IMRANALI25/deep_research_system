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

def create_solo_agent(file_format: HC.FileFormat, research_topic: str) -> Agent:
    
# Initialize  Variables
    INSTRUCTIONS = """You are the Expert Deep Research Assistant.You always
        perform deep research according to the given topic {research_topic}. 
        Always focused on the given topic {research_topic} only.
        Always use the user’s query exactly, without rewriting it.
        You always discard irrelevant content from web search output. 
        You orchestrate all tasks including Gather all the relevant requirements, 
        plan a summarized query for deep research, web searching, 
        synthesizing the findings and report generation.
        The report must be detailed, comprehensive,contains images, tables, 
        animations and having comparative analysis, provide in depth knowledge
        and information about the research topic.
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

    try:
        # 🎁 Model Settings For Orchestrator Agent
        MODEL_SETTINGS = ModelSettings(
            temperature=1.5,
            top_p=0.75,
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
            
        # 🕵🏽 Create Solo Agent
        solo_agent: Agent = Agent(
            name="solo_agent",
            model=LP.LLM_MODEL,
            instructions=f"{INSTRUCTIONS}\n\n{SPECIAL_INSTRUCTIONS}",
            tools=[],
            model_settings=MODEL_SETTINGS,
        )
        if solo_agent is None:
            print("🤖 Solo Agent could not be created.")
            exit(1)
        else:
            return solo_agent
    except OpenAIError as e:
        print(f"❌ [OPENAI ERROR] Unexpected client error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ [UNKNOWN ERROR - Solo Agent] {type(e).__name__}: {e}")
        exit(1)
