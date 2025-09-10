from pydantic import BaseModel
from abc import ABC
from typing import Any
from abc import abstractmethod
import random

from tsiipa.translate.tools_syntax import ToolCallExample


def get_random_tool_call_id():
    """Generate a random tool call id of the form call_aSENunZCF31ob7zV89clvL4n"""
    return "call_" + ''.join(random.choices(characters, k=24))

class FewShotExample(BaseModel):
    user_input: str
    tool_calls: list[ToolCallExample]
    bot_response: str

class FewShot(ABC):
    @abstractmethod
    def create_few_shot_messages(self):
        pass
        
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass


class CreateFewShotMessages()
