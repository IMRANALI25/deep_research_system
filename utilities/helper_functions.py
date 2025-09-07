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
    topics,
)

import datetime, time, sys, os
import random
from typing import Union, List, Dict
import json

# DELAYED TYPING PARAMETERS
def delayed_print(
    text: Union[str, List[str]] | None,
    delay: float = 0.00006,
    char_by_char: bool = True,
    line_delay: float = None,
):
    """
    Print text (or multiple lines) with delays.

    Args:
        text (str | list[str]): Single string or list of strings to print.
        delay (float): Base delay in seconds.
                       If char_by_char=True → delay per character.
                       If char_by_char=False → delay after each print.
        char_by_char (bool): If True, prints like typing effect.
        line_delay (float): Extra delay between lines (if list is passed).
                            Defaults to delay if not provided.
    """
    if isinstance(text, str):
        lines = [text]
    else:
        lines = text

    for line in lines:
        if char_by_char:
            for char in line:
                print(char, end="", flush=True)
                time.sleep(delay)
            print()  # move to next line
        else:
            print(line, flush=True)

        # Delay after each line
        time.sleep(line_delay if line_delay is not None else delay)


# 🤠INITIALIZE USER FOR LOCAL CONTEXT OBJECT
def get_user_profile():
    return UP.UserContext()


def get_deep_research_topic() -> str:
    try:
        delayed_print("\n🙋 Enter the Research Topic. [Press 𝒒 to quit 🚪🏃]:}")
        CC.RESEARCH_TOPIC = input()

        if not CC.RESEARCH_TOPIC:
            delayed_print(
                "🖊️ No research topic is provided.\n🕵️‍♂️ Agent will choose any one of tht topic from below mentioned list..."
            )

            for i, topic in enumerate(topics.DEEP_RESEARCH_TOPICS, start=1):
                delayed_print(f"{i:>03}. 📑 {topic}")

            topic_index = random.randint(0, len(topics.DEEP_RESEARCH_TOPICS) - 1)
            CC.RESEARCH_TOPIC = topics.DEEP_RESEARCH_TOPICS[topic_index]
            # pass
        elif CC.RESEARCH_TOPIC == "q":
            delayed_print("🕵️‍♂️ Agent is exiting from deep research task...")
            exit(0)

        delayed_print(f"\n 🢃 Deep 🔬 Research 📑 Topic 📋 ➢➢➤➤ {CC.RESEARCH_TOPIC}")
        return CC.RESEARCH_TOPIC
    except Exception as e:
        print(f"❌ [ ERROR - helper_functions.py - get_deep_research_topic()] {type(e).__name__}: {e}")
        exit(1)


def get_file_path(research_topic: str, file_format: HC.FileFormat):
    # Get current date & time
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Define folder path
        folder = "C:/Research_Reports"  # Windows style
        # Create folder if it doesn’t exist
        os.makedirs(folder, exist_ok=True)

        report_name = (research_topic)[0:80]
        # Replace special characters
        for ch in ["?", ":", "/", "*", "<", ">", "|", '"', "\\", " "]:
            report_name = report_name.replace(ch, "_")

        # Build md filename
        report_name = f"{report_name}_{timestamp}.{file_format.value.lower()}"

        file_path = os.path.join(folder, report_name)
        return report_name, file_path
    except Exception as e:
        print(f"❌ [ERROR helper_functions.py -  get_file_path()] {type(e).__name__}: {e}")
        exit(1)

# @function_tool
def get_md_report(final_output, research_topic):
    try:
        report_name, file_path = get_file_path(research_topic, HC.FileFormat.MD)

        md_content = f"# {research_topic} \n\n"

        if isinstance(final_output, dict):
            for key, value in final_output.items():
                md_content += f"## {key}\n"
                if isinstance(value, (dict, list)):
                    md_content += f"```json\n{json.dumps(value, indent=2)}\n```\n\n"
                else:
                    md_content += f"{value}\n\n"
        elif isinstance(final_output, list):
            md_content += "## Items\n"
            for idx, item in enumerate(final_output, 1):
                md_content += f"- **Item {idx}:** {item}\n"
        else:
            md_content += str(final_output)

        # return md_content 
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        delayed_print(
            f"📘 Research Report in 📑 MarkDown format is saved 📀 as {report_name}",
        )

        delayed_print(
            f"🗂️ File Path: 📂 {file_path}",
        )

        delayed_print("🍔" * 60)
        delayed_print(
            f"""\n⮞⮞⮞⮞⮞  📜✍️  The Final Report for
📰 {research_topic[0:100]}
✒️  Generated Successfully  💯🏆🎯 and Saved 📀
to 📂 {file_path}   ⮜⮜⮜⮜⮜ \n""")
        delayed_print("🍔" * 60,)

    except PermissionError as e:
        print(
            f"❌ Error: You don’t have permission to write to {report_name}. {e}"
        )
        exit(1)
    except Exception as e:
        print(f"❌ [ERROR helper_functions.py - get_md_report()] {type(e).__name__}: {e}")
        exit(1)


# @function_tool
def get_html_report(final_output, research_topic):
    try:
        report_name, file_path = get_file_path(research_topic, HC.FileFormat.HTML)
        start_marker = "<!DOCTYPE html>"
        end_marker = "</html>"

        # Find starting index
        start_index = final_output.find(start_marker)
        if start_index == -1:
            return "Error: <!DOCTYPE html> not found."

        # Find ending index
        end_index = final_output.find(end_marker, start_index)
        if end_index == -1:
            return "Error: </html> not found."

        # Include the </html> tag in output
        end_index += len(end_marker)

        delayed_print("🕵️‍♂️ Agent is generating HTML document...")

        html_output = final_output[start_index:end_index]
        # PRINT ONLY HTML
        # print(html_output)

        if html_output.startswith("Error:"):
            print(html_output)  # If error message, just print it
            return
                
        delayed_print(
            f"\n🌐 Creating 👉 HTML Formatted Report for 📜 {research_topic}\n",
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_output)

        delayed_print(
            f"📘 Research Report in 🌐 HTML format is saved 📀 as {report_name}",
        )

        delayed_print(
            f"🗂️ File Path: 📂 {file_path}",
        )

        delayed_print("🍔" * 60)
        delayed_print(
            f"""\n⮞⮞⮞⮞⮞  📜✍️  The Final Report for
📰 {research_topic[0:100]}
✒️  Generated Successfully  💯🏆🎯 and Saved 📀
to 📂 {file_path}   ⮜⮜⮜⮜⮜ \n""")
        delayed_print("🍔" * 60)

    except PermissionError as e:
        print(
            f"❌ Error: You don’t have permission to write to '{html_format_report}'. {e}"
        )
        exit(1)
    except Exception as e:
        print(f"❌ [ ERROR helper_functions.py - get_html_report()] {type(e).__name__}: {e}")
        exit(1)


def set_console_header(ctx_user_name: str, research_topic: str):
    print("\n")
    delayed_print("🟧" * 50)
    delayed_print(
        f"🤵  User {ctx_user_name} \n",
    )

    delayed_print(
        f"🟧" * 50,
    )
    print("\n")

    delayed_print(
        f"""🕵️‍♂️  Agent Starting the Deep Research Process 🔂➤➤➤➤➤\n""",
    )

    delayed_print(
        f"""📕 Deep Research Topic  ⮞⮞⮞⮞⮞ 📜 {research_topic}    ⮜⮜⮜⮜⮜ \n""",
    )
    delayed_print("🌐" * 50)
    print("\n")

    delayed_print("⭐" * 50)
    print("\n")

    delayed_print(
        """🕵️‍♂️🕵️‍♂️  AI Agents are  🤔💭 Thinking, 🔍 Searching, 🔬 Analyzing, 
        🎻🎺🎷 Synthesizing and finalizing ✒️ the Research Report 📊.""",
    )
    delayed_print(
        "🕸️ Searching the WEB.......🕸️",
    )

    # delayed_print(
    #     "⏳⏳⏳  Please Wait... ⏳⏳⏳",
    # )

    delayed_print("⭐" * 50)

    print("\n")
    delayed_print("📌" * 50)

    delayed_print(
        f"""        🛠️  Final Report 👉 For 📜 [{research_topic}]
                    💡  is Generating ➤➤➤ NOW...💡""",
    )
    delayed_print("📌" * 50)
    print("\n")


def transform_response_data(response):
    emojis_header_bar("⭐", number_of_emojis=50)

    print(f"\n🔎 Query: {response['query']}\n")
    print(f"\n✅ Answer: {response['answer']}\n")

    for i, result in enumerate(response["results"], start=1):
        # console.print(
        #     f"{i}. {result['title']}", style="bold red on yellow", justify="center"
        # )
        print(f"{i}. {result['title']}")
        print(f"   📌 URL: {result['url']}")
        # CONST.LIST_OF_URLS.append({result["url"]})
        print(f"   📝 Content: {result['content']}")
        # print(f"   📊 Raw Data: {result['raw_content']}")

    print(f"   ⏳ Response Time: {response['response_time']}")

    emojis_header_bar("⭐", number_of_emojis=40)


def get_llm_client_model():
    try:
        # ⚙️ INITIALIZE LLM SERVICE CLIENT
        LP.LLM_ASYNC_CLIENT: AsyncOpenAI = AsyncOpenAI(
            api_key=LP.GEMINI_API_KEY,
            base_url=LP.GEMINI_BASE_URL,
        )

        # 🎲 INITIALIZE LLM MODEL USING CHAT COMPLETIONS MODEL
        LP.LLM_MODEL: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
            model=LP.SELECTED_MODEL, openai_client=LP.LLM_ASYNC_CLIENT
        )
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
    except OpenAIError as e:
        print(f"❌[OPENAI ERROR] Unexpected client error: {e}")
        exit(1)
    except ImportError as e:
        print(f"❌ [Import ERROR] Cannot Import File: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ [ERROR - helper_functions.py - get_llm_client_model() ] {type(e).__name__}: {e}")
        exit(1)


def get_runner_input(selected_agent_name: str, research_topic: str) -> str:
    INPUT_TO_RUNNER = ""
    try:
        match selected_agent_name:
            
            case "solo_agent":
                INPUT_TO_RUNNER = f"""You are the Expert Deep Research Assistant. 
                    Generate a deep research report of {research_topic}. 
                    You always perform deep research according to the given topic {research_topic}.                                        
                    You must gathered all requirements from web searching.
                    You must create a summarized technical query, do web searching,
                    synthesize, verify and validate the findings sources. 
                    """
            case "tavily_client_agent":
                INPUT_TO_RUNNER = f"""You are the Expert Deep Research Assistant. 
                    Generate a deep research report of {research_topic}. 
                    You always perform deep research according to the given topic {research_topic}.                    
                    Always use Tavily Web Services to gathering all requirements for web searching.
                    You must create a summarized technical query, do web searching,
                    synthesize, verify and validate the findings sources. 
                    """
                    
        return INPUT_TO_RUNNER
    except Exception as e:
        print(f"❌ [ERROR - helper_functions.py - get_runner_input()] {type(e).__name__}: {e}")
        exit(1)
        
        
def pretty_print(obj, indent=0):
    """Recursively pretty-print dicts/lists from JSON objects."""
    spacing = "  " * indent
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{spacing}{key}:")
            pretty_print(value, indent + 1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            print(f"{spacing}- [{i}]")
            pretty_print(item, indent + 1)
    else:
        print(f"{spacing}{obj}")


def emojis_header_bar(emoji: str = "🟠", number_of_emojis: int = 30):
    print(f"{emoji}" * number_of_emojis)


def emojis_header_bar_with_Info(
    message: str,
    emoji: str = "🟠",
    start_number_of_emojis: int = 15,
    end_number_of_emojis: int = 15,
):
    print(f"{emoji * start_number_of_emojis} {message} {emoji * end_number_of_emojis}")


###################################################################################
# Extract JSON Dict from final Output


# def extract_data_from_response():
#     try:
#         parts = result.final_output.split("```")
#         print(parts)

#         for i, part in enumerate(parts):
#             if part.strip().startswith("json"):
#                 # Remove 'json' and keep the actual JSON content
#                 json_str = part.replace("json", "", 1).strip()
#                 # return json.loads(json_str)

#         print("📌" * 50)
#         print(json_str)

#         with open("electric_car_benefits.json", "w", encoding="utf-8") as f:
#             json.dump(json_str, f, indent=4, ensure_ascii=False)

#         print("✅ JSON extracted and saved as 'electric_car_benefits.json'")
#         print(json.dumps(json_str, indent=2, ensure_ascii=False))

#     except json.JSONDecodeError as e:
#         print("Error parsing JSON:", e)
#         exit(1)

###################################################################################

################################################################################
# SPECIAL PROMPT
# async def special_prompt(
#     special_context: RunContextWrapper[UserContext], agent: Agent[UserContext]
# ) -> str:

#     return f"""{CONST.SPECIAL_INSTRUCTIONS}\n You should use report and summary tools.
#                 Always save the report to context and handoff to Lead Agent.
#                 User: {special_context.context.user_name},
#                 Agent: {agent.name}"""


# Dynamic Instructions
# def dynamic_instructions(
#     local_context: RunContextWrapper[UserContext], agent: Agent[UserContext]
# ) -> str:
#     # Access conversation messages
#     messages = getattr(local_context, "messages", [])
#     message_count = len(messages)

#     return f"""You are {agent.name} with {len(agent.tools)} tools.
#                 You are an experienced assistant that can do research
#                 in any field of science and technology.
#                 You are facilitating deep research services to,
#                 {local_context.context.user_name}
#                 has preferences including {local_context.context.user_preferences}.
#                 The local time is {datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")},
#                 This is the message #{message_count} in our conversation.
#                 Be helpful and informative!"""
################################################################################
