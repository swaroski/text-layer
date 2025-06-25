from typing import Dict, List
from flask import current_app
from app import logger
from app.core.commands import ReadCommand
from app.errors import ValidationException
from app.services.llm.prompts.chat_prompt import chat_prompt
from app.services.llm.session import LLMSession
from app.services.llm.tools.text_to_sql import text_to_sql as text_to_sql_tool
from app.utils.formatters import get_timestamp
from langfuse.decorators import observe
from openai import BadRequestError
from vaul import Toolkit
from uuid import uuid4
import json


from app.services.llm.vector.faiss_schema_retriever import retrieve_schema_context


class ProcessChatMessageCommand(ReadCommand):
    """
    Process a chat message.
    """

    def __init__(self, chat_messages: List[Dict[str, str]]) -> None:
        self.chat_messages = chat_messages
        self.llm_session = LLMSession(
            chat_model=current_app.config.get("CHAT_MODEL"),
            embedding_model=current_app.config.get("EMBEDDING_MODEL"),
        )
        self.toolkit = Toolkit()
        self.toolkit.add_tools(text_to_sql_tool)

    def validate(self) -> None:
        if not self.chat_messages:
            raise ValidationException("Chat messages are required.")
        return True

    def execute(self) -> List[Dict]:
        
        logger.debug(f'Command {self.__class__.__name__} started with {len(self.chat_messages)} messages.')

        self.validate()

        chat_kwargs = {
            "messages": self.prepare_chat_messages(),
            "tools": self.toolkit.tool_schemas(),
        }       

        try:
            response = self.llm_session.chat(**chat_kwargs)

            logger.debug(f"LLM finish_reason: {response.choices[0].finish_reason}")
            logger.debug(f"LLM tool_calls: {getattr(response.choices[0].message, 'tool_calls', None)}")
        except BadRequestError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to fetch chat response: {e}")
            raise ValidationException("Error in fetching chat response.")

        tool_messages = []

        response_message_config = {
            "role": "assistant",
            "content": response.choices[0].message.content,
            "finish_reason": response.choices[0].finish_reason,
        }

        if response.choices[0].finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls

            response_message_config["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in tool_calls
            ]

            response_message = self.format_message(**response_message_config)

            for tool_call in tool_calls:
                  
                tool_result = self.execute_tool_call(tool_call)

                # Ensure tool_result is always a JSON-serializable dict
                if hasattr(tool_result, "dict"):
                    content = tool_result.dict()
                elif hasattr(tool_result, "model_dump"):
                    content = tool_result.model_dump()
                elif hasattr(tool_result, "json"):
                    content = json.loads(tool_result.json())
                elif isinstance(tool_result, dict):
                    content = tool_result
                else:
                    content = str(tool_result)

                tool_message = self.format_message(
                    role="tool",
                    tool_call_id=tool_call.id,
                    content=json.dumps(content)  # Always JSON-safe
                )

               

                tool_messages.append(tool_message)
        else:
            response_message = self.format_message(**response_message_config)

        # Append all messages
        self.chat_messages.append(response_message)
        self.chat_messages.extend(tool_messages)

        return self.chat_messages

    @observe()
    def prepare_chat_messages(self) -> List[Dict]:
        trimmed = self.llm_session.trim_message_history(self.chat_messages)
        # ⬇️ Inject schema context for latest user message
        latest_user_message = next(
            (msg for msg in reversed(self.chat_messages) if msg["role"] == "user"), None
        )
        if latest_user_message:
            schema_context = retrieve_schema_context(latest_user_message["content"])
        else:
            schema_context = []
        # ⬇️ Strict prompt with schema context injected
        system_prompt = chat_prompt(schema_context=schema_context)
        return system_prompt + trimmed

    @observe()
    def format_message(self, role: str, content: str, **kwargs) -> Dict:
        return {
            "id": str(uuid4()),
            "role": role,
            "content": content,
            "timestamp": (get_timestamp(with_nanoseconds=True),),
            **kwargs,
        }

    @observe()
    def execute_tool_call(self, tool_call: dict) -> dict:
        result = self.toolkit.run_tool(
            name=tool_call.function.name,
            arguments=json.loads(tool_call.function.arguments),
        )
        # Robustly convert various possible result shapes to dict
        if hasattr(result, "dict"):
            return result.dict()
        if hasattr(result, "model_dump"):  # Pydantic v2
            return result.model_dump()
        if hasattr(result, "json"):  # Fallback for Pydantic v1/v2
            return json.loads(result.json())
        if isinstance(result, dict):
            return result
        # Fallback: try str
        return {"value": str(result)}