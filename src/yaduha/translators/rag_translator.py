import time
from typing import Dict, List, Tuple, Optional, Any
from yaduha.translators import Translator, Translation
from yaduha.tools import Tool
from yaduha.common import get_openai_client
import openai
from yaduha.tools.search import SearchEnglishTool, SearchSentencesTool
from yaduha.bots import Bot


class RAGTranslator(Translator):
    model: str = "gpt-4o-mini"
    tools: List[Tool] = [SearchEnglishTool(), SearchSentencesTool()]
    name: str = "rag_translator"
    description: str = "Translate text to the target language using retrieval-augmented generation (RAG) with a set of tools."
    
    # System messages for translation context
    prompt: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": 
                """You are a language translator for the language known as Owen's Valley Paiute. \n
                You will answer a direct translation for a sentence provided by the user.\n
                The user is a beginner eager to learn Paiute translations. You have access to several tools:\n
                - **English word search:** Translate words and phrases from English to Paiute.\n
                - **semantic search:** Given an English sentence, retrieve similar Paiute translations to provide context and improve accuracy.\n
                - **split_stentence:** Given a complex english sentence (ex. I saw two men walking their dogs yesterday at Starbucks while drinking a cup of coffee), split it into simple sentences (Subject-Verb-Object (SVO) or Subject-Verb (SV) format) to make it easier to translate (I saw two men. The men were walking their dogs. The men were drinking coffee.).\n
                - **Simple senttence translator:** Use simple sentence translator function to help in developing the grammatically correct sentence in Paiute.\n
                You can use the following grammar rules to check user input sentences from English to Owens Valley Paiute in addition to the other tools available to you.\n
                Use the vocabulary and sentence structures available to translate the input sentence as best as possible.\n
                It doesn't need to be perfect and you can leave English words untranslated if necessary.\n"""
        }
    ]
    
    def __call__(self, sentence: str) -> Translation:
        bot = Bot(
            client=get_openai_client(),
            model=self.model,
            tools=self.tools,
            description=self.description,
            
        )
        response= bot(messages=[{"role": "user", "content": sentence}])
        print(response)
        return Translation(
            source=sentence,
            target=response,
            back_translation=None,
            translation_prompt_tokens=1,
            translation_completion_tokens=1,
            translation_time=1.0,
            back_translation_prompt_tokens=1,
            back_translation_completion_tokens=1,
            back_translation_time=1.0
        )


    def get_examples(self, sentences: List[str] = ["I drink water"]) -> List[Tuple[Dict, Translation]]:
            examples = [
                ({"sentence": sentence}, self(sentence=sentence)) for sentence in sentences
            ]
            return examples        