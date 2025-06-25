from app.commands.threads.process_chat_message import ProcessChatMessageCommand
from app.controllers.controller import Controller

class ThreadController(Controller):
    """
    A controller for threads.
    """
    def process_chat_message(self, chat_messages: list) -> list:
        """
        Processes a chat message using the ProcessChatMessageCommand.
        Returns the chat history including LLM and tool messages.
        """
        # If your executor has execute_read, use that for non-mutating operations.
        # If not, execute_write is fine as long as it calls command.execute().
        return self.executor.execute_read(ProcessChatMessageCommand(chat_messages))
