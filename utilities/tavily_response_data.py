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
)
from tavily import (
    AsyncTavilyClient,
    MissingAPIKeyError,
    InvalidAPIKeyError,
    UsageLimitExceededError,
    BadRequestError,
)

from typing import List, Optional
from pydantic import BaseModel
import os, json, itertools, asyncio, typing
import datetime, time
from dataclasses import dataclass
import asyncio
from utilities import (
    api_keys as AK,
    helper_functions as HF,
    llm_parameters as LP,
    config_constants as CC,
    user_profile as UP,
    helper_classes as HC,
)


# ----------------------------
# 1. Define Pydantic Models
# ----------------------------

class TavilyResultModel(BaseModel):
    title: str
    url: str
    content: str
    score: float
    raw_content: Optional[str] = None
    favicon: Optional[str] = None

class TavilyResponseModel(BaseModel):
    query: str
    results: List[TavilyResultModel]
    answer: Optional[str] = None
    images: Optional[List[str]] = []
    response_time: Optional[float] = None
    requestId: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None

# ----------------------------
# 2. Define Dataclasses
# ----------------------------
@dataclass
class TavilyResultDC:
    title: str
    url: str
    content: str
    score: float
    raw_content: Optional[str] = None
    favicon: Optional[str] = None

@dataclass
class TavilyResponseDC:
    query: str
    results: List[TavilyResultDC]
    answer: Optional[str] = None
    images: Optional[List[str]] = None
    response_time: Optional[float] = None
    requestId: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None

# ----------------------------
# Transform Data Helper Function
# ----------------------------


async def transform_parsed_data(parsed_data,  tavily_client: AsyncTavilyClient) -> List[dict]:
    try:
        HF.emojis_header_bar("⭐", number_of_emojis=50)

        print(f"\n🔎  Query: {parsed_data['query']}\n")
        print(f"\n✅  Answer: {parsed_data['answer']}\n")

        for i, result in enumerate(parsed_data["results"], start=1):
            print(f"{i:>2}. {result['title']}")
            print(f"📌 URL: {result['url']}")
            print(f"🎯 Score: {result['score']}")
            if result["score"] > 0.5:
                CC.LIST_OF_URLS.append({result["url"]})
            print(f"📝  Content: {result['content']}")
            # print(f"📊  Raw Data: {result['raw_content']}")

        print(f"⏳ Response Time: {parsed_data['response_time']}")

        # Extract content from the relevant URLs
        extracted_data = await asyncio.gather(*(tavily_client.extract(url) for url in CC.LIST_OF_URLS))

        HF.emojis_header_bar("⭐", number_of_emojis=40)
        return extracted_data
    except Exception as e:
        print(f"❌ [ERROR - tavily_response_data.py : transform_parsed_data()] {type(e).__name__}: {e}")
        exit(1)
# ---------------------------------
# Tavily Results Helper Function
# ---------------------------------


async def get_tavily_results(
    raw_response: Optional[dict] = None,
    tavily_client: AsyncTavilyClient = None,
    use_pydantic: bool = True
) -> List[dict]:
    try:
        data = None
        # ----------------------------
        # Parse JSON into Pydantic Model
        # ----------------------------
        if use_pydantic:
            # parse directly into Pydantic
            # return TavilyResponseModel(**raw_response)
            parsed_pydantic = TavilyResponseModel(**raw_response)
            data = await transform_parsed_data(parsed_pydantic, tavily_client)
        else:
            # Convert results list to dataclass objects
            results_dc = [TavilyResultDC(**res) for res in raw_response.get("results", [])]
            parsed_dc = TavilyResponseDC(
                query=raw_response["query"],
                results=results_dc,
                answer=raw_response.get("answer"),
                images=raw_response.get("images"),
                response_time=raw_response.get("response_time"),
                requestId=raw_response.get("requestId"),
                follow_up_questions=raw_response.get("follow_up_questions")
            )
            data = await transform_parsed_data(parsed_dc, tavily_client)
            
        return data
    except Exception as e:
        print(f"❌ [ERROR - tavily_response_data.py : get_tavily_results()] {type(e).__name__}: {e}")
        exit(1)
