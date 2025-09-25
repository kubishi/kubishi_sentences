from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Any, List


class ToolCallExample(BaseModel):
    tool_name: str
    tool_description: str
    tool_parameters: dict
    tool_response: Any

class Tool(ABC):
    @abstractmethod
    def get_examples(self) -> List[ToolCallExample]:
        pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass

class SearchEnglishTool(Tool):
    def get_examples(self) -> List[ToolCallExample]:
        return [
            ToolCallExample(
                tool_name="search_english",
                tool_description="Search for a term in English",
                tool_parameters={"query": "dog"},
                tool_response={"results": ["dog", "doge"]}
            )
        ]

    def execute(self, *args, **kwargs) -> Any:
        query = kwargs.get("query", "")
        # Perform search operation
        return {"results": ["dog", "doge"]}
