from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from yaduha.tools import Tool


class Translation(BaseModel):
    source: str
    target: str
    back_translation: Optional[str]

    prompt_tokens: int
    completion_tokens: int
    translation_time: float
    back_translation_prompt_tokens: int
    back_translation_completion_tokens: int
    back_translation_time: float
    metadata: Dict[str, Any] = {}

    def __str__( self ) -> str:
        lines = [
            f"Source: {self.source}",
            f"Target: {self.target}",
            f"Back Translation: {self.back_translation}",
            f"Prompt Tokens: {self.prompt_tokens}",
            f"Completion Tokens: {self.completion_tokens}",
            f"Translation Time: {self.translation_time:.2f} seconds",
            f"Back Translation Prompt Tokens: {self.back_translation_prompt_tokens}",
            f"Back Translation Completion Tokens: {self.back_translation_completion_tokens}",
            f"Back Translation Time: {self.back_translation_time:.2f} seconds",
        ]
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return self.__str__()

class Translator(Tool):
    model: str
    tools: List[Tool]
    name: str = "translator"
    description: str = "Translate text to the target language and back to the source language."
    
    def __call__(self, text: str) -> Translation:
        """Translate the text to the target language and back to the source language.
        
        Args:
            text (str): The text to translate.
        Returns:
            Translation: The translation
        """
        raise NotImplementedError
