import json
import time
import logging
from pydantic import BaseModel


from yaduha.common import get_openai_client
from yaduha.translate.base import Translation, Translator
from yaduha.translate.ablation.translation_functions import split_sentence_tool, translate_simple_sentences, translate_sentence
from yaduha.translate.ablation.ablation_tools import pipeline_tools, instructions_pipeline_messages
from openai.types.chat import ChatCompletion

client = get_openai_client()

functions = {
    "split_sentence": split_sentence_tool,
    "translate_simple_sentence": translate_simple_sentences
}

class InstructionsPipelineTranslator(Translator):
    def __init__(self, model: str):
        self.model = model

    def translate(self, sentence: str) -> Translation:
        
        start = time.time()
        response = translate_sentence(sentence, model=self.model, functions=functions, example_messages=instructions_pipeline_messages, tools=pipeline_tools)
        end = time.time()
        time_taken = end - start
        translation = Translation(
            source=sentence,
            target=response["translation"],
            back_translation="",
            translation_prompt_tokens=response["translation_prompt_tokens"],
            translation_completion_tokens=response["translation_completion_tokens"],
            translation_total_tokens=response["translation_total_tokens"],
            translation_time=time_taken,
            back_translation_prompt_tokens=0,
            back_translation_completion_tokens=0,
            back_translation_total_tokens=0,
            back_translation_time=0.0,
            metadata={
                "messages": json.dumps(response["messages"], ensure_ascii=False),
                "model": self.model,
            }
        )

        return translation