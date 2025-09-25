from yaduha.translators import Translator, Translation
from yaduha.tools import Tool
from typing import List

class PipelineTranslator(Translator):
    tools: List[Tool] = []
    name: str = "pipeline_translator"
    description: str = "Translate text to the target language and back to the source language using a pipeline of tools."

    def __call__(self, text: str) -> Translation:
        raise NotImplementedError

