##########################################################################################
# User Enters Deep Research Topic# U
# Agent gathered all the requirements about the topic from  the web
# Then Handoff to planning agent
##########################################################################################
import os, json, itertools, asyncio, typing
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
from agents.items import MessageOutputItem
from dotenv import load_dotenv, find_dotenv
from tavily import (
    AsyncTavilyClient,
    MissingAPIKeyError,
    InvalidAPIKeyError,
    UsageLimitExceededError,
    BadRequestError,
)
import utility_functions as uf
from UserProfile import UserContext
import datetime, time
from dataclasses import dataclass
import constants as CONST
from rich.console import Console

# 🤠INITIALIZE USER FOR LOCAL CONTEXT OBJECT
USR_ALI = UserContext()

# 🔣 LOAD ENVIRONMENT VARIABLES
load_dotenv(find_dotenv())
# 🔎 Enable/Disable Tracing
set_tracing_disabled(disabled=True)

try:
    # 🔑 Load Keys
    CONST.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    CONST.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
except Exception as e:
    print(" API Key error - main.py:", {e})
    exit(1)


# 🤵Initialize Tavily Client Object
tavily_client = AsyncTavilyClient(api_key=CONST.TAVILY_API_KEY)

# ⚛️🔬 Deep Research Topic
CONST.RESEARCH_TOPIC = uf.get_deep_research_topic()

try:
    # ⚙️ Initialize LLM Service
    client: AsyncOpenAI = AsyncOpenAI(
        api_key=CONST.GEMINI_API_KEY,
        base_url=CONST.GEMINI_BASE_URL,
    )

    # 🎲 Initialize LLM Model using Chat Completions Model
    model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
        model=CONST.SELECTED_MODEL, openai_client=client
    )

# === Specific Exceptions ===
except AuthenticationError as e:
    print(f"❌ [AUTH ERROR] Invalid or missing API key: {e}")
    exit(1)
except PermissionDeniedError as e:
    print(f"❌ [PERMISSION ERROR] Access denied: {e}")
    exit(1)
except RateLimitError as e:
    print(f" ❌[RATE LIMIT ERROR] Too many requests: {e}")
    exit(1)
except NotFoundError as e:
    print(f" ❌[NOT FOUND ERROR] Resource missing: {e}")
    exit(1)
except BadRequestError as e:
    print(f"❌ [BAD REQUEST ERROR] Invalid parameters: {e}")
    exit(1)
except APIConnectionError as e:
    print(f"❌ [CONNECTION ERROR] Network problem: {e}")
    exit(1)
except APIStatusError as e:
    print(f"❌ [API STATUS ERROR] HTTP {e.status_code}: {e.response}")
    exit(1)
# === Catch-all OpenAI Error ===
except OpenAIError as e:
    print(f"❌[OPENAI ERROR] Unexpected client error: {e}")
    exit(1)
except ImportError as e:
    print(f"❌ [Import ERROR] Cannot Import File: {e}")
    exit(1)
# === Fallback for anything else ===
except Exception as e:
    print(f"❌ [UNKNOWN ERROR - main.py] {type(e).__name__}: {e}")
    exit(1)


# 🧰 Search Function Tool
@function_tool
async def tavily_deep_search(
    local_context: RunContextWrapper[UserContext],
    query: str,
) -> str:
    try:
        print(
            f" 🌐 Deep research starting, requested by 🤵{local_context.context.user_name} for: [ 🙋 {query} 🙋] "
        )

        response = await tavily_client.search(
            query,
            auto_parameters=True,
            search_depth="advanced",
            topic="general",
            max_results=3,
            include_raw_content=True,
            include_answer=True,
        )

        print("🟠" * 50)
        print("\n")
        # print(
        #     f""" 📑✒️ Formatting Response Data using Tavily Web Search for
        #     🤵{local_context.context.user_name}""",
        # )

        # Human Readable Format on Terminal
        # uf.transform_response_data(response)

        # return data
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
        print(f"❌ [UNKNOWN ERROR - research_agent.py] {type(e).__name__}: {e}")
        exit(1)


# 🕵🏽 Create Requirement Gathering Agent
try:
    instructions_to_agent = f"""You are the genius and expert deep research assistant. 
        Search the web extensively, plan the content in a structured way.
        Always perform synthesized activity, you must filter, verify and validate the data. 
        Summarize findings when required. Then create a final professional report."""

    solo_agent: Agent = Agent(
        name="Requirement_Elicitation_Agent",
        model=model,
        instructions=instructions_to_agent,
        tools=[tavily_deep_search],
        model_settings=ModelSettings(
            temperature=1.0,
            top_p=0.9,
            tool_choice="none",
            parallel_tool_calls=False,
        ),
    )
# === Catch-all OpenAI Error ===
except OpenAIError as e:
    print(f"❌ [OPENAI ERROR] Unexpected client error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ [UNKNOWN ERROR - planning_agent.py] {type(e).__name__}: {e}")
    exit(1)


async def main():

    input_to_runner = f""" Step 1 - Gather all the relevant requirements of {CONST.RESEARCH_TOPIC} for deep research.
        Step 2 - Use all requirements from Step 1, create a detailed technical query that includes all aspects of the topic: {CONST.RESEARCH_TOPIC}.
        Step 3 - Use the Query from Step 2, thoroughly deep research from the web using tavily web service with the help of function tool.
        Step 4 - After web searching, Create a Research Report of at least 10-15 pages, for the topic {CONST.RESEARCH_TOPIC}.
        Step 5 - The report must be detailed, comprehensive, having comparative analysis, provide in depth knowledge and information about the research topic,
        Step 6 - The report must be full of creativity, innovation and professional. 
        Step 7 - The report must be designed like a 'Responsive WEB Page' using CSS3 rules and HTML5 tags.
        Step 8 - The report can use CSS, HTML frameworks like TAILWINDCSS, BOOTSTRAP, BULMA for best user experience.
        Step 9 - The report may be used Javascript for user interaction, if required.
        Step 10 - The report must be well structured, contains images, tables, animations and must be human readable and eye catching. 
        Step 11 - Use Colorful Headings and Subheadings of maximum 4 levels deep.       
        Step 12 - Subheadings hierarchy levels should be like this (Heading 1 -> SubHeading LEVEL 1.1 -> SubHeading LEVEL 1.1.1).         
        Step 13 - Always create complete CSS3 style and HTML5 document structure in a single output report.        
        Step 14 - Text Content must use nice font family and different font sizes as per heading requirement.
        Step 15 - Include Lazy Loading with animated text and graphics in the report using CSS3 rules.
        Step 16 - In Header and Footer of HTML Report Document, always add current System DAte and Time. 
        Step 17 - Always Use bold, italic and underline for text emphasis.
        Step 18 - Save this report in '.html' format on the PC.        
        Step 19 - The generated Report must be beautifully formatted in HTML document as a final output.
        """
    ctx = RunContextWrapper(UserContext())

    uf.set_console_header(ctx.context.user_name, CONST.RESEARCH_TOPIC)

    result = await Runner.run(
        starting_agent=solo_agent,
        input=input_to_runner,
        context=ctx,
    )

    final_output = "\n".join(result.final_output.split("\n"))
    uf.get_final_html_report(
        final_output,
        CONST.RESEARCH_TOPIC,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as run_error:
        print(f"❌ Runtime error while running model: {run_error}")
        exit(1)


######################################################################################################################
    # print("\n=== result.to_input_list() ===")
    # print(result.to_input_list())
    #
    #
    # print(result.final_output)
    # print("\n=== FINAL OUTPUT SPLITTED ===")
    # print(result.final_output.split("\n"))
    # print("📌" * 50)
    # print("\n=== CONTEXT DATA ===")
    # print(ctx.context)
    # print("📌" * 50)
    # print(json.loads(result.final_output.split("\n")))

    # print("\n=== Parsed Data..... ===")
    # parsed = json.dumps(result.final_output, indent=2).split("\n")
    # print("🔹 Parsed Final Output (Nested View):")
    # uf.pretty_print(parsed)
    # print("\n=== JSON Formatted Data..... ===")
    #
    #
    # print("\n".join(result.final_output.split("\n")))
############################################################################################################################    