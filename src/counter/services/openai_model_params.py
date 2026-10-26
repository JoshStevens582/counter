from typing import Any


def responses_api_kwargs(model: str) -> dict[str, Any]:
    if model.startswith("gpt-6-"):
        return {"reasoning": {"effort": "none"}}
    return {"temperature": 0}
