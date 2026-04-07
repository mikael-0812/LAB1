import inspect
import os
from typing import Any, Dict, List, Tuple

import tools
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.core.openai_provider import OpenAIProvider
from src.telemetry.logger import logger

TEST_CASES = [
    {
        "id": "TC01",
        "description": "Fashion price lookup",
        "input": "What is the price of T-Shirt Basic in fashion store?"
    },
    {
        "id": "TC02",
        "description": "Course prerequisite check",
        "input": "What are the prerequisites for Course 1?"
    },
    {
        "id": "TC03",
        "description": "Restaurant opening hours",
        "input": "Is Restaurant 1 open?"
    },
    {
        "id": "TC04",
        "description": "Travel flight price",
        "input": "What is the flight price to Destination?"
    },
    {
        "id": "TC05",
        "description": "Bank account balance",
        "input": "What is the balance of ACC001?"
    },
]

_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-1.5-flash",
    "google": "gemini-1.5-flash",
    "local": os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
}

SUPPORTED_BASELINE_KEYWORDS = [
    "fashion",
    "áo",
    "quần",
    "giày",
    "course",
    "khóa học",
    "môn học",
    "restaurant",
    "nhà hàng",
    "quán ăn",
    "travel",
    "du lịch",
    "đặt vé",
    "bank",
    "ngân hàng",
    "tài khoản",
    "github",
    "repo",
    "issue",
]


def get_default_model(provider: str) -> str:
    return _DEFAULT_MODELS.get(provider.lower(), _DEFAULT_MODELS["openai"])


def initialize_provider(provider: str, model_name: str):
    provider = provider.lower()
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        return OpenAIProvider(model_name=model_name, api_key=api_key)
    if provider in {"gemini", "google"}:
        api_key = os.getenv("GEMINI_API_KEY")
        return GeminiProvider(model_name=model_name, api_key=api_key)
    if provider == "local":
        return LocalProvider(model_path=model_name)
    raise ValueError(f"Unknown provider: {provider}")


def _build_tool_registry() -> List[Dict[str, Any]]:
    tool_names = [
        "check_out_of_stock",
        "discount",
        "price",
        "search_fashion",
        "prerequisite_check",
        "elective_check",
        "course_price",
        "credit_count",
        "optimize_plan",
        "is_open",
        "average_price",
        "location_search",
        "flight_price",
        "hotel_availability",
        "discount_package",
        "check_balance",
        "loan_interest",
        "currency_exchange",
        "create_github_issue",
        "get_github_repo_info",
        "list_github_issues",
    ]

    registry: List[Dict[str, Any]] = []
    for name in tool_names:
        func = getattr(tools, name, None)
        if not callable(func):
            continue
        doc = inspect.getdoc(func) or "No description available."
        registry.append({
            "name": name,
            "description": doc.splitlines()[0].strip(),
            "func": func,
        })
    return registry


def _baseline_has_support(user_input: str) -> bool:
    query = user_input.lower()
    return any(keyword in query for keyword in SUPPORTED_BASELINE_KEYWORDS)


def run_baseline(llm, user_input: str) -> str:
    if not _baseline_has_support(user_input):
        return "[UNSUPPORTED] This query is outside the baseline domain."

    system_prompt = (
        "You are a simple baseline assistant for the lab. Answer questions directly and concisely. "
        "If the question is outside fashion, course, restaurant, travel, banking, or GitHub domains, reply exactly with [UNSUPPORTED]."
    )
    response = llm.generate(user_input, system_prompt=system_prompt)
    return response.get("content", "").strip()


def run_agent_with_trace(llm, user_input: str) -> Tuple[str, List[str]]:
    tools_registry = _build_tool_registry()
    agent = ReActAgent(llm=llm, tools=tools_registry)
    answer = agent.run(user_input)
    return answer, agent.trace_lines
