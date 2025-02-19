from infuzu import create_chat_completion, ChatCompletionsHandlerRequestMessage
from dotenv import load_dotenv


load_dotenv()


messages = [
    ChatCompletionsHandlerRequestMessage(role="system", content="You are a helpful assistant."),
    ChatCompletionsHandlerRequestMessage(role="user", content="What is the capital of France?"),
]


try:
    response = create_chat_completion(messages=messages)
    print(response)
except Exception as e:
    print(f"Error: {e}")
