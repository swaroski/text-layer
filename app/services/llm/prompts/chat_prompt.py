from app.services.llm.prompts import prompt
from typing import Any


@prompt()
def chat_prompt(**kwargs: Any) -> list[dict[str, str]]:
    """
    Generate a system prompt for LLM chat interactions.

    Parameters:
        kwargs (dict): Keyword arguments to dynamically populate prompt content.
            Example: chat_prompt(name="Alex", tone="friendly")

    Returns:
        list of dict: A list of messages formatted for an LLM chat interface.
    
    Example:
        >>> chat_prompt(name="Alex", tone="friendly")
        [
            {"role": "system", "content": "You are a helpful assistant named Alex. Respond in a friendly tone."}
        ]

    Notes:
        You can customize the content by passing in variables, which are substituted
        using Python string formatting (`%(key)s`).
    """
    return [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant"
                f"{' named %(name)s' if 'name' in kwargs else ''}."
                f"{' Respond in a %(tone)s tone.' if 'tone' in kwargs else ''}"
            ) % kwargs
        }
    ]
