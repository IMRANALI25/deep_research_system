from tavily import AsyncTavilyClient
from dotenv import load_dotenv, find_dotenv
import os

from utilities import (
    api_keys as AK,
    helper_functions as HF,
    llm_parameters as LP,
    config_constants as CC,
    user_profile as UP,
)


# This module is used to initialize all keys for this project
# 🔣 LOAD ENVIRONMENT VARIABLES
def get_env_variables() -> None:
    try:
        load_dotenv(find_dotenv())
    except Exception as e:
        print(f"❌ Could not load .env file: {e}")
        exit(1)


# 🔑 Load Keys
# 🔐 Assign Gemini API Key to local variable
def get_gemini_key() -> str:
    try:
        gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    except ValueError as ve:
        print(f"❌ GEMINI_API_KEY is not set/found in environment variable!!!  {ve}")
    except Exception as e:
        print(f" Unexpected error: {e}")

    return gemini_api_key


# 🔐 Assign Tavily API Key to local variable
def get_tavily_key() -> str:
    try:
        tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")

    except ValueError as ve:
        print(f" ❌ TAVILY_API_KEY is not set/found in environment variable!!! {ve}")
    except Exception as e:
        print(f" Unexpected error: {e}")

    return tavily_api_key


# 🔑 Load Keys
# 🔐 Assign API Key to variable
def get_api_key(SELECTED_API_KEY: str | None) -> str:
    try:
        if SELECTED_API_KEY is not None:
            match SELECTED_API_KEY:
                case "GEMINI_API_KEY":
                    return os.getenv("GEMINI_API_KEY")
                case "OPENAI_API_KEY":
                    return os.getenv("OPENAI_API_KEY")
                case "TAVILY_API_KEY":
                    return os.getenv("TAVILY_API_KEY")
                case _:
                    return "API KEY Not Available"
    except ValueError as ve:
        print(
            f"❌ {SELECTED_API_KEY} is not set/found in environment variable!!!  {ve}"
        )
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)
