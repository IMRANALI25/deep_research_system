from typing import Union, List, Dict
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

# CONSTANTS VARIABLES DECLARATION AND INITIALIZATION
# BASE URLs
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

OPENAI_BASE_URL = ""

# GEMINI MODELS VARIANTS
GEMINI_MODEL_2_5_FLASH = "gemini-2.5-flash"
GEMINI_MODEL_1_5_FLASH = "gemini-1.5-flash"
GEMINI_MODEL_2_5_FLASH_LITE = "gemini-2.5-flash-lite"
GEMINI_MODEL_2_5_PRO = "gemini-2.5-pro"

# OPENAI MODELS
OPENAI_MODEL_4 = "gpt-4"
OPENAI_MODEL_3_5 = "gpt-3.5-turbo"

# USER SELECTED MODEL
SELECTED_MODEL = GEMINI_MODEL_2_5_FLASH

# 🔑 DECLARE API KEY VARIABLES
GEMINI_API_KEY: str | None
TAVILY_API_KEY: str | None
OPENAI_API_KEY: str | None

# ⚙️ LLM SERVICE VARIABLE
LLM_ASYNC_CLIENT = None

# 🎲 LLM MODEL VARIABLE USING CHAT COMPLETIONS MODEL
LLM_MODEL = None

# 🔣🛠️ MODEL SETTING CLASS PARAMETERS
# 🔥TEMPERATURE Controls randomness in responses.
# Higher values (e.g., 1.0–1.5) → more creative;
# lower values (0–0.5) → more deterministic.
TEMPERATURE: float = 0.6
# ⚛️ Nucleus sampling. The model considers tokens with cumulative
# probability up to top_p. Typical range: 0–1.
TOP_P: float = 0.6
# 𝕄𝕒𝕩💯 Maximum number of tokens the model can generate in a single response.
# 𝕄𝕒𝕩💯 The range of max_tokens depends on the model: Gemini-2.5-flash / other large models Varies, usually 8192–32768
MAX_TOKENS: int = 8192
# ⚽️🥅 Penalizes new tokens based on their existing frequency in the text so far. Range: 0–2.
# ❌ Gemini doesn’t support this
FREQUENCY_PENALTY: float = 0.4
# ⚽️🥅 Penalizes new tokens based on whether they appear in the text at all. Range: 0–2.
# ❌ Gemini doesn’t support this
PRESENCE_PENALTY: float = 0.4
# 🛑 List of stop sequences to terminate the model’s output.
STOP: List[str] = None
# 💃🏻 Name of the model (e.g., "gpt-4", "gpt-4o-mini", "gpt-3.5-turbo").
MODEL_NAME: str = SELECTED_MODEL
# ✔️ Which tool the agent can use ("none", "auto", "required","<tool_name>").
TOOL_CHOICE: str = "None"
# ⏸☎️ If True, allows the agent to run multiple tools in parallel.
PARALLEL_TOOL_CALLS: bool = False
# ✂ (Optional) Gradually reduce randomness over multiple agent steps.
TEMPERATURE_DECAY: float = 0.0
# 🔄Maximum number of retries if a tool or model call fails.
MAX_RETRIES: int = 1

MODEL_SETTINGS = ModelSettings(
    temperature=TEMPERATURE,
    top_p=TOP_P,
    max_tokens=MAX_TOKENS,
    stop=STOP,
    model_name=MODEL_NAME,
    tool_choice=TOOL_CHOICE,
    parallel_tool_calls=PARALLEL_TOOL_CALLS,
    temperature_decay=TEMPERATURE_DECAY,
    max_retries=MAX_RETRIES,
)
