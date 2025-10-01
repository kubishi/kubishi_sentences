import requests
from typing import Dict, List, Tuple, ClassVar

from yaduha.tools import Tool
from yaduha.translators.pipeline_translator import PipelineTranslator

#Questions to ask:
#What is limit for? Do I need to use it to limit the amount of responses? or examples?
class PipelineTranslate(Tool):
    name: str = "translate_sentence"
    description: str = "translate a sentence from english to paiute using pipeline translator, always grammatically correct"

    def __call__(self, query: str, limit: int) -> str:
        return PipelineTranslator()(query).target
    
    def get_examples(self, sentences: List[str] = ["I drink water"], limit: int = 5) -> List[Tuple[Dict, List[Dict]]]:
        examples = [
            ({"query": sentence, "limit": limit}, self(query=sentence, limit=limit)) for sentence in sentences
        ]
        return examples
    