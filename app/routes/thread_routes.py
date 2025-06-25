from flask import Blueprint, request, jsonify, Response, stream_with_context
import uuid
import time
import logging
from app.commands.threads.process_chat_message import ProcessChatMessageCommand

thread_routes = Blueprint('thread_routes', __name__)

logger = logging.getLogger(__name__)

def generate_correlation_id():
    return str(uuid.uuid4())

@thread_routes.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    logger.info("Received /chat request")
    logger.debug(f"Messages: {messages}")

    try:
        cmd = ProcessChatMessageCommand(messages)
        payload = cmd.execute()
        logger.debug(f"LLM/Tool payload: {payload}")
    except Exception as e:
        logger.error(f"Error in ProcessChatMessageCommand: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

    response = {
        "correlation_id": generate_correlation_id(),
        "payload": payload,
        "status": 200
    }
    return jsonify(response), 200

@thread_routes.route('/chat/stream', methods=['POST'])
def chat_stream():
    data = request.json
    messages = data.get('messages', [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    logger.info("Received /chat/stream request")
    logger.debug(f"Messages: {messages}")

    try:
        cmd = ProcessChatMessageCommand(messages)
        print("CMD", cmd)
        payload = cmd.execute()
        logger.debug(f"LLM/Tool payload: {payload}")
    except Exception as e:
        logger.error(f"Error in ProcessChatMessageCommand: {e}", exc_info=True)
        yield f"data: [ERROR] {str(e)}\n\n"
        return

    def event_stream():
        # Stream only assistant/tool messages
        for message in payload:
            if message.get("role") in {"assistant", "tool"}:
                # Stream each message as a "chunk"
                yield f"data: {message['content']}\n\n"
                time.sleep(0.1)
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(event_stream()), mimetype='text/event-stream')