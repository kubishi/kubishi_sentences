import json
import time
import logging
from pydantic import BaseModel


from yaduha.common import get_openai_client
from yaduha.translate.base import Translation, Translator
from yaduha.chatbot.tools.functions import search_english, search_sentences
from yaduha.translate.ablation.ablation_tools import rag_tools, rag_instruction_messages
from yaduha.translate.ablation.translation_functions import translate_sentence
from openai.types.chat import ChatCompletion

client = get_openai_client()

functions = {
    "search_english": search_english,
    "search_sentences": search_sentences,
}

class RagInstructionsTranslator(Translator):
    def __init__(self, model: str):
        self.model = model

    def translate(self, sentence: str) -> Translation:
        start = time.time()
        response = translate_sentence(sentence, model=self.model, functions=functions, example_messages=rag_instruction_messages, tools=rag_tools)
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