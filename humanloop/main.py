import asyncio
import datetime
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from autogen_core import (
    CancellationToken,
    DefaultInterventionHandler,
    DefaultTopicId,
    FunctionCall,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    message_handler,
    type_subscription,
)

from autogen_core.model_context import BufferedChatCompletionContext

from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    SystemMessage,
    UserMessage,        
)

from autogen_core.tools import BaseTool
from pydantic import BaseModel, Field
import yaml

@dataclass
class TextMessage:
    source: str
    content: str

@dataclass
class UserTextMessage(TextMessage):
    pass

@dataclass
class AssistantTextMessage(TextMessage):
    pass

@dataclass
class GetSlowUserMessage:
    pass

@dataclass
class TerminateMessage:
    content: str

class MockPersistence:
    def __init__(self):
        self._content: Mapping[str, Any] = {}

    def load_content(self) -> Mapping[str, Any]:
        return self._content

    def save_content(self, content: Mapping[str, Any]) -> None:
        self._content = content

state_persister = MockPersistence()

@type_subscription("scheduling_assistant_conversation")
class SlowUserProxyAgent(RoutedAgent):
    def __init__(
        self, 
        name: str, 
        description: str,        
    ) -> None:
        super().__init__(description)
        self._model_context = BufferedChatCompletionContext(
            buffer_size=5
        )
        self._name = name

    @message_handler
    async def handle_message(
        self,
        message: AssistantTextMessage,
        context: MessageContext,
    ) -> None:
        await self._model_context.add_message(AssistantMessage(
            content=message.content,
            source=message.source
        ))
        await self.publish_message(
            GetSlowUserMessage(content=message.content), topic_id=DefaultTopicId("scheduling_assistant_conversation")
        )

    async def save_state(self) -> Mapping[str, Any]:
        state_to_save = {
            "memory": await self._model_context.save_state(),
        }
        return state_to_save

    async def load_state(self, state: Mapping[str, Any]) -> None:
        await self._model_context.load_state(state["memory"])

class ScheduleMeetingInput(BaseModel):
    recipient: str = Field(description="Name of recipient")
    date: str = Field(description="Date of the meeting")
    time: str = Field(description="Time of the meeting")

class ScheduleMeetingOutput(BaseModel):
    pass

class ScheduleMeetingTool(BaseTool[ScheduleMeetingInput, ScheduleMeetingOutput]):
    def __init__(self):
        super().__init__(
            ScheduleMeetingInput,
            ScheduleMeetingOutput,
            "schedule_meeting",
            "Schedules a meeting with the recipient at the specified date and time",    
        )

    async def execute(self, args: ScheduleMeetingInput, cancellation_token: CancellationToken) -> ScheduleMeetingOutput:
        # Simulate scheduling logic
        print(f"Meeting scheduled with {args.recipient} on {args.date} at {args.time}.")
        return ScheduleMeetingOutput()
    
@type_subscription("scheduling_assistant_conversation")
class SchedulingAssistant(RoutedAgent):
    def __init__(
        self, 
        name: str, 
        description: str,
        model_client: ChatCompletionClient,
        initial_message: AssistantMessage | None = None,        
    ) -> None:
        super().__init__(description)
        self._model_context = BufferedChatCompletionContext(
            buffer_size=5,
            initial_message=[UserMessage(
                content=initial_message.content, source=initial_message.source)]
            if initial_message else None,
        )
        self._name = name
        self._model_client = model_client
        self._system_message = [
            SystemMessage(
                content=f"""
I am a helpful AI assistant that helps schedule meetings.
If there are missing parameters, I will ask for them.

Today's date is {datetime.datetime.now().strftime("%Y-%m-%d")}
"""
            )
        ]

    @message_handler
    async def handle_message(
        self,
        message: UserTextMessage,
        context: MessageContext,
    ) -> None:
        await self._model_context.add_message(UserMessage(
            content=message.content,
            source=message.source
        ))

        tools = [ScheduleMeetingTool()]
        response = await self._model_client.create(
            self._system_message + (await self._model_context.get_messages()),
            tools=tools,
        )
        
        if isinstance(response.content, list) and all(isinstance(item, FunctionCall) for item in response.content):
            
        
      