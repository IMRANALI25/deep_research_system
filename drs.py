##########################################################################################
#
#Deep Research System Orchestrator
#
##########################################################################################

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
from utilities import (
    api_keys as AK,
    helper_functions as HF,
    llm_parameters as LP,
    config_constants as CC,
    user_profile as UP,
    helper_classes as HC,
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
from research_agents import requirement_agent as RA
import os, json, itertools, asyncio, typing
import datetime, time
from dataclasses import dataclass


async def main():    
    try:
        
        # 🚀 Initialize Parameters

        # 🔣 LOAD ENVIRONMENT VARIABLES
        AK.get_env_variables()

        # 🔎 Enable/Disable Tracing
        set_tracing_disabled(disabled=False)

        # 🤠INITIALIZE USER OBJECT
        user = HF.get_user_profile()

        # 🧊INITIALIZE CONTEXT OBJECT
        ctx = RunContextWrapper(user)

        # 🔑 Load Keys
        LP.GEMINI_API_KEY = AK.get_api_key("GEMINI_API_KEY")
        LP.TAVILY_API_KEY = AK.get_api_key("TAVILY_API_KEY")

        # 👨🏻‍💻 Initialize Tavily Client Object
        tavily_client = AsyncTavilyClient(api_key=LP.TAVILY_API_KEY)

        # ⚛️🔬 Deep Research Topic
        CC.RESEARCH_TOPIC = HF.get_deep_research_topic()

        # ⚙️ INITIALIZE LLM SERVICE CLIENT
        # 🎲 INITIALIZE LLM MODEL USING CHAT COMPLETIONS MODEL
        HF.get_llm_client_model()

        INPUT_TO_RUNNER = HF.get_runner_input("tavily_client_agent", CC.RESEARCH_TOPIC)
                        
        HF.set_console_header(ctx.context.user_name, CC.RESEARCH_TOPIC)

        HF.delayed_print("🤖 Agent Creating...")

        # Create Separate Agents for HTML and MD format reports
        # starting_agent = SA.create_solo_agent(HC.FileFormat.MD, CC.RESEARCH_TOPIC)
        # starting_agent2 = SA.create_solo_agent(HC.FileFormat.HTML, CC.RESEARCH_TOPIC)        
        # starting_agent = TA.create_tavily_client_agent(HC.FileFormat.MD, CC.RESEARCH_TOPIC)
        # starting_agent2 = TA.create_tavily_client_agent(HC.FileFormat.HTML, CC.RESEARCH_TOPIC)

        starting_agent = RA.create_requirement_agent(HC.FileFormat.MD, CC.RESEARCH_TOPIC)
        starting_agent2 = RA.create_requirement_agent(HC.FileFormat.HTML, CC.RESEARCH_TOPIC)
        HF.delayed_print(f"🕵 {starting_agent.name} created...")
        HF.delayed_print("🏃 Agent Start Running...")
        HF.delayed_print(f"""🌐 Deep Research Starting, requested by 🤵{ctx.context.user_name}""")        
        HF.delayed_print(
            f"""🕵️‍♂️  Agent ✍️  Finalizing the 📀 data about 
Deep Research Report: {CC.RESEARCH_TOPIC}"...\n
✍️  Writing a dynamic report will take some time 🕒.""")

        HF.delayed_print("""\n⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞⮞
        ⌛ Please, Wait... 📕✒️  Report Writer is Working on it.🪄📖✨  
⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜⮜""")        

        TA.last_user_query = CC.RESEARCH_TOPIC

        # Create HTML format report
        # result_html = await Runner.run(
        #     starting_agent=starting_agent2,
        #     input=INPUT_TO_RUNNER,
        #     context=ctx,
        # )
        # time.sleep(100)

        result_md = await Runner.run(
            starting_agent=starting_agent,
            input=INPUT_TO_RUNNER,
            context=ctx,
        )

        # HF.delayed_print("🥩📄🗞📜 Raw Output Data......")
        # print(result_md.final_output)

        # HF.delayed_print("🗐✒️ Generating HTML Report......📑")
        # final_output_html = "\n".join(result_html.final_output.split("\n"))
        # HF.get_html_report(
        #     final_output_html,
        #     CC.RESEARCH_TOPIC,
        # )
        # time.sleep(100)

        HF.delayed_print("🗐✒️ Generating MarkDown Report......📑")
        final_output_md = "\n".join(result_md.final_output.split("\n"))

        HF.delayed_print("🗐✒️ Print Report on Console......📑")
        print(result_md.final_output)
        # time.sleep(100)
        HF.get_md_report(final_output_md, CC.RESEARCH_TOPIC,)

        # print(final_output_html)
        # print(final_output_md)

    except Exception as e:
        print(f"❌ [Runner Error - drs.py - main()] {type(e).__name__}: {e}")
        exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as run_error:
        print(f"❌ Runtime error while running model: {run_error}")
        exit(1)
