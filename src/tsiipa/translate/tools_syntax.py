from pydantic import BaseModel
from abc import ABC
from typing import Any, List
from abc import abstractmethod

class ToolCallExample(BaseModel):
    tool_name: str
    tool_description: str
    tool_parameters: dict
    tool_response: Any

class ToolCallArgument(BaseModel):
    name: str
    type: str
    description: str

#Ask what properties we need to make dynamic and which ones should be static
class ToolCallFunction(BaseModel):
    tool_name: str
    tool_description: str
    arguments: List[ToolCallArgument]

    def create_function(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "strict": True,
                "parameters": {
                    "type": "object",
                    "required": [
                        "query"
                    ],
                    "properties": {
                        arg.name: {
                            "type": arg.type,
                            "description": arg.description
                        }
                        for arg in self.arguments
                    },
                    "additionalProperties": False
                }
            }
        }
        


class Tool(ABC):
    @abstractmethod
    def get_examples(self) -> list[ToolCallExample]:
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass

class SearchEnglishTool(Tool):
    def get_examples(self) -> list[ToolCallExample]:
        return [ToolCallExample(
            tool_name="Search English",
            tool_description="Searches for a word in English",
            tool_parameters={"query": "dog"},
            tool_response={"results": ["dog", "doge"]},
        )]
    
    def execute(self) -> Any:
        query = kwargs.get("query", "")

        return {"results": ["dog", "doge"]}
    