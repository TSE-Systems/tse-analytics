from typing import Any

import lmstudio as lms

SERVER_API_HOST = "localhost:1234"
# This must be the *first* convenience API interaction (otherwise the SDK
# implicitly creates a client that accesses the default server API host)
lms.configure_default_client(SERVER_API_HOST)


def lms_running() -> bool:
    if lms.Client.is_valid_api_host(SERVER_API_HOST):
        print(f"An LM Studio API server instance is available at {SERVER_API_HOST}")
        return True
    else:
        print("No LM Studio API server instance found at {SERVER_API_HOST}")
        return False


def lms_get_response(
    model_name: str,
    prompt: str,
    system_prompt: list[dict[str, Any]],
    initial_history: list[dict[str, Any]],
) -> lms.PredictionResult:
    model = lms.llm()
    # Create a chat with an initial system prompt.
    initial_prompt = system_prompt[0]["text"]
    history = {
        "messages": [
            {"role": "system", "content": initial_prompt},
        ]
    }
    for message in initial_history:
        history["messages"].append(message)
    chat = lms.Chat.from_history(history)
    # chat.add_user_message(prompt)
    # The `chat` object is created in the previous step.
    result = model.respond(chat)
    return result
