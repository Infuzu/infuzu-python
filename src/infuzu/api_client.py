import platform
import time
import uuid
import httpx
import os
from typing import (Optional, Dict, Union, List)
from pydantic import (BaseModel, validator, Field, ConfigDict, model_validator)
from .utils import get_version
from .errors import InfuzuAPIError


class ModelWeights(BaseModel):
    model_config = ConfigDict(extra="allow")

    price: Optional[float] = None
    error: Optional[float] = None
    start_latency: Optional[float] = None
    end_latency: Optional[float] = None


class InfuzuModelParams(BaseModel):
    model_config = ConfigDict(extra="allow")

    llms: Optional[List[str]] = None
    exclude_llms: Optional[List[str]] = None
    weights: Optional[ModelWeights] = None
    imsn: Optional[int] = None
    max_input_cost: Optional[float] = None
    max_output_cost: Optional[float] = None


class ChatCompletionsRequestContentPart(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    text: Optional[str] = None
    image_url: Optional[str] = None
    input_audio: Optional[str] = None

    @model_validator(mode='after')
    def check_content_fields(self) -> 'ChatCompletionsRequestContentPart':
        if self.type == "text" and self.text is None:
            raise ValueError("Text must be provided when type is 'text'")
        if self.type != "text" and self.text is not None:
            raise ValueError("Text cannot be provided when type is not 'text'")
        return self


class ChatCompletionsHandlerRequestMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    content: Union[str, List[ChatCompletionsRequestContentPart]]
    role: str
    name: Optional[str] = None

    @model_validator(mode='after')
    def role_must_be_valid(self) -> 'ChatCompletionsHandlerRequestMessage':
        if self.role not in ('system', 'user', 'assistant'):
            raise ValueError('Role must be one of: system, user, assistant')
        return self


class ChatCompletionsChoiceMessageAudioObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    expired_at: Optional[int] = None
    data: Optional[str] = None
    transcript: Optional[str] = None


class ChatCompletionsChoiceMessageFunctionCallObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    arguments: Optional[str] = None


class ChatCompletionsChoiceMessageToolCallFunctionObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    arguments: Optional[str] = None


class chatCompletionsChoiceMessageToolCallObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    type: Optional[str] = None
    function: Optional[ChatCompletionsChoiceMessageToolCallFunctionObject] = None


class ChatCompletionsChoiceMessageObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    content: Optional[str] = None
    refusal: Optional[str] = None
    tool_calls: Optional[List[chatCompletionsChoiceMessageToolCallObject]] = None
    role: Optional[str] = None
    function_call: Optional[ChatCompletionsChoiceMessageFunctionCallObject] = None
    audio: Optional[ChatCompletionsChoiceMessageAudioObject] = None


class ChatCompletionsChoiceLogprobsItemTopLogprobObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    token: Optional[str] = None
    logprob: Optional[int] = None
    bytes: Optional[List[int]] = None


class ChatCompletionsLogprobsItemObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    token: Optional[str] = None
    logprob: Optional[int] = None
    bytes: Optional[List[int]] = None
    content: Optional[List[ChatCompletionsChoiceLogprobsItemTopLogprobObject]] = None


class ChatCompletionsChoiceLogprobsObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    content: Optional[List[ChatCompletionsLogprobsItemObject]] = None
    refusal: Optional[List[ChatCompletionsLogprobsItemObject]] = None


class ChatCompletionsChoiceModelObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    ref: Optional[str] = None
    rank: Optional[int] = None


class ChatCompletionsChoiceErrorObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    message: Optional[str] = None
    code: Optional[str] = None


class ChatCompletionsChoiceLatencyObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    start: Optional[int] = Field(None, alias='start_latency')
    end: Optional[int] = Field(None, alias='end_latency')


class ChatCompletionsChoiceObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    finish_reason: Optional[str] = None
    index: Optional[int] = None
    message: Optional[ChatCompletionsChoiceMessageObject] = None
    logprobs: Optional[ChatCompletionsChoiceLogprobsObject] = None
    model: Optional[ChatCompletionsChoiceModelObject] = None
    error: Optional[ChatCompletionsChoiceErrorObject] = None
    latency: Optional[ChatCompletionsChoiceLatencyObject] = None


class ChatCompletionsObject(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    choices: Optional[List[ChatCompletionsChoiceObject]] = None
    created: Optional[int] = None
    model: Optional[str] = None
    service_tier: Optional[str] = None
    system_fingerprint: Optional[str] = None
    object: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


API_BASE_URL: str = "https://chat.infuzu.com/api"


def create_chat_completion(
        messages: List[ChatCompletionsHandlerRequestMessage],
        api_key: Optional[str] = None,
        model: Optional[Union[str, InfuzuModelParams]] = None,
) -> ChatCompletionsObject:
    """
    Creates a chat completion using the Infuzu API.

    Args:
        messages: A list of message objects.
        api_key: Your Infuzu API key. If not provided, it will be read from the
                 INFUZU_API_KEY environment variable.
        model: The model to use for the chat completion. Can be a string (model name)
                or a InfuzuModelParams object for more advanced configuration.

    Returns:
        The ChatCompletionsObject Object

    Raises:
        ValueError: If the API key is not provided and the INFUZU_API_KEY
                    environment variable is not set.
        InfuzuAPIError: If the API request returns an error status code.
    """

    if api_key is None:
        api_key: str | None = os.environ.get("INFUZU_API_KEY")
        if api_key is None:
            raise ValueError(
                "API key not provided and INFUZU_API_KEY environment variable not set."
            )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Infuzu-API-Key": api_key,
        "User-Agent": (
            f"infuzu-python/{get_version()} "
            f"(Python {platform.python_version()}; "
            f"httpx/{httpx.__version__}; "
            f"{platform.system()} {platform.release()})"
        )
    }

    payload: dict[str, any] = {
        "messages": [message.model_dump(by_alias=True) for message in messages],
    }

    if model:
        if isinstance(model, str):
            payload["model"] = model
        else:
            payload["model"] = model.model_dump(by_alias=True)

    try:
        with httpx.Client() as client:
            response: httpx.Response = client.post(
                f"{API_BASE_URL}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=600
            )

        response.raise_for_status()
        json_response: dict[str, any] = response.json()

        json_response.setdefault('id', f"chatcmpl-{uuid.uuid4()}")
        json_response.setdefault('created', int(time.time()))
        json_response.setdefault('model', 'infuzu-ims')
        json_response.setdefault('object', 'chat.completion')

        return ChatCompletionsObject(**json_response)
    except httpx.HTTPStatusError as e:
        raise InfuzuAPIError(e)
