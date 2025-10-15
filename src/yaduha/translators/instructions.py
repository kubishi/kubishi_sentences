import time
from typing import Dict, List, Tuple, Optional, Any
from yaduha.translators import Translator, Translation
from yaduha.tools import Tool
from yaduha.common import get_openai_client
from yaduha.tools.search import SearchEnglishTool, SearchSentencesTool
from yaduha.bots import Bot
from yaduha.translators.pipeline.pipeline_sentence_builder import LENIS_MAP, NOUNS, Verb, Subject, Object


class InstructionsTranslator(Translator):
    model: str = "gpt-4o-mini"
    tools: List[Tool] = [SearchEnglishTool(), SearchSentencesTool()]
    name: str = "Instructions_translator"
    description: str = "Translate text to the target language using instructions with a set of tools."
    
    # System messages for translation context
    prompt: str =(
        "You use the following grammar rules to translate user input sentences from English to Owens Valley Paiute.\n" + 
        "Use the vocabulary and sentence structures available to translate the input sentence as best as possible.\n" +
        "It doesn't need to be perfect and you can leave English words untranslated if necessary.\n" +
        # section on vocabulary
        "# Vocabulary\n" +
        "## Nouns: \n" + "\n".join([f"{ovp}: {eng}" for ovp, eng in NOUNS.items()]) + "\n" +
        "## Transitive Verbs: \n" + "\n".join([f"{ovp}: {eng}" for ovp, eng in Verb.TRANSITIVE_VERBS.items()]) + "\n" +
        "## Intransitive Verbs: \n" + "\n".join([f"{ovp}: {eng}" for ovp, eng in Verb.INTRANSITIVE_VERBS.items()]) + "\n" +
        "## Object Suffixes: \n" + "\n".join([f"{ovp}: {eng}" for ovp, eng in Object.SUFFIXES.items()]) + "\n" +
        "## Object Pronouns: \n" + "\n".join([f"{ovp}: {eng}" for ovp, eng in Object.PRONOUNS.items()]) + "\n" +
        "## Subject Suffixes: \n" + "\n".join([f"{ovp}: {eng}" for ovp, eng in Subject.SUFFIXES.items()]) + "\n" +
        "## Subject Pronouns: \n" + "\n".join([f"{ovp}: {eng}" for ovp, eng in Subject.PRONOUNS.items()]) + "\n" +
        "## Verb Nominalizer Tenses: \n" + "\n".join([f"{ovp}: {eng}" for ovp, eng in Verb.NOMINALIZER_TENSES.items()]) + "\n" +
        "\n# Sentence Structure\n" + # next section on sentence structure
        "## Simple Sentence Structure: \n" +
        "Subject-Object-Verb: [object noun]-[object suffix] [subject noun]-[subject suffix] [object pronoun]-[verb]-[verb tense]\n" +
        "Subject Pronoun-Object-Verb: [object noun]-[object suffix] [subject pronoun] [object pronoun]-[verb]-[verb tense]\n" +
        "Subject-Verb: [verb]-[verb tense] [subject noun]-[subject suffix]\n" +
        "## Verb Nominalization Sentence Structure: \n" +
        "Subject Nominalizer: [verb]-[verb nominalizer tense]-[subject suffix] [verb nominalizer]-[verb nominalizer tense]\n" +
        "Object Nominalizer: [verb]-[verb nominalizer tense]-[object suffix] [subject noun]-[subject suffix] [object pronoun]-[verb]-[verb tense]\n" +
        "Subject&Object Nominalizer: [verb]-[verb nominalizer tense]-[object suffix] [verb nominalizer]-[verb nominalizer tense]-[subject suffix] [subject noun]-[subject suffix] [object pronoun]-[verb]-[verb tense]\n" +
        "\n# Fortis/Lenis Transformations\n" + # next section on fortis/lenis transformations
        ", ".join([f"{f}->{l}" for f, l in LENIS_MAP.items()]) + "\n""It doesn't need to be perfect and you can leave English words untranslated if necessary.\n"
    )
    def __call__(self, sentence: str) -> Translation:
        start = time.time()
        bot = Bot(
            client=get_openai_client(),
            model=self.model,
            tools=self.tools,
            description=self.description,
        )
        response = bot(
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": sentence}
            ]
        )

        end = time.time()
        return Translation(
            source=sentence,
            target=response.response,
            back_translation=None,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            translation_time=end - start,
            back_translation_prompt_tokens=0,
            back_translation_completion_tokens=0,
            back_translation_time=0.0
        )

    def get_examples(self) -> List[Tuple[Dict, Any]]:
        return []
