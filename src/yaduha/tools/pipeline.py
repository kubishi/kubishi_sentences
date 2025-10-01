from typing import Dict, List, Tuple

from yaduha.tools import Tool
from yaduha.translators.pipeline import PipelineTranslator

class PipelineTranslate(Tool):
    name: str = "translate_sentence"
    description: str = "translate a sentence from english to paiute using pipeline translator, always grammatically correct"

    def __call__(self, query: str) -> str:
        return PipelineTranslator()(query).target
    
    def get_examples(self, sentences: List[str] = ["I drink water"]) -> List[Tuple[Dict, str]]:
        examples = [
            ({"query": sentence}, self(query=sentence)) for sentence in sentences
        ]
        return examples
    