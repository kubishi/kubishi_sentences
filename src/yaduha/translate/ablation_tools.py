import json
import pathlib

from yaduha.translate.pipeline_sentence_builder import LENIS_MAP, NOUNS, Verb, Subject, Object

thisdir = pathlib.Path(__file__).parent.absolute()

rag_tools = [
    #search English ----------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "search_english",
            "description": "Search for Paiute words in English (semantic search).",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": [
                    "query"
                ],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term, either a word or a sentence."
                    },
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_sentences",
            "description": "Search for sentences in English (semantic search).",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": [
                    "query"
                ],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term, either a word or a sentence."
                    },
                },
                "additionalProperties": False
            }
        }
    },
]

pipeline_tools = [
    {
        "type": "function",
        "function": {
            "name": "split_sentence",
            "description": "Given a complex english sentence (ex. I saw two men walking their dogs yesterday at Starbucks while drinking a cup of coffee), split it into simple sentences (Subject-Verb-Object (SVO) or Subject-Verb (SV) format) to make it easier to translate (I saw two men. The men were walking their dogs. The men were drinking coffee.).\n",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": [
                    "sentence"
                ],
                "properties": {
                    "sentence": {
                        "type": "string",
                        "description": "A complex english sentence."
                    },
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "translate_simple_sentence",
            "description": "Translates simple sentences (Subject-Verb-Object (SVO) or Subject-Verb (SV) from English to Owen's Valley Paiute in accurate grammar.\n",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": [
                    "sentence"
                ],
                "properties": {
                    "sentence": {
                        "type": "string",
                        "description": "A list of simple english sentences."
                    },
                },
                "additionalProperties": False
            }
        }
    }
]

#Full Translator ----------------------------------------------------
system_prompt_full = (
    "You are a language translator for the language known as Owen's Valley Paiute. \n" + 
    "You will answer a direct translation for a sentence provided by the user.\n" +
    "The user is a beginner eager to learn Paiute translations. You have access to several tools:\n" + 
    "- **English word search:** Translate words and phrases from English to Paiute.\n" +
    "- **semantic search:** Given an English sentence, retrieve similar Paiute translations to provide context and improve accuracy.\n" + 
    "- **split_stentence:** Given a complex english sentence (ex. I saw two men walking their dogs yesterday at Starbucks while drinking a cup of coffee), split it into simple sentences (Subject-Verb-Object (SVO) or Subject-Verb (SV) format) to make it easier to translate (I saw two men. The men were walking their dogs. The men were drinking coffee.).\n" +
    "- **Simple senttence translator:** Use simple sentence translator function to help in developing the grammatically correct sentence in Paiute.\n" +
    "You can use the following grammar rules to check user input sentences from English to Owens Valley Paiute in addition to the other tools available to you.\n" + 
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
    ", ".join([f"{f}->{l}" for f, l in LENIS_MAP.items()]) + "\n"
)

full_translation_messages = json.loads((thisdir / "few_shot/full_translator/full_translator_messages.json").read_text())
full_translation_messages.insert(0, {"role": "system", "content": system_prompt_full})

# RAG instructions translator ------------------------------------------------------------------------

system_prompt_RAG_instructions = (
    "You are a language translator for the language known as Owen's Valley Paiute. \n" + 
    "You will answer a direct translation for a sentence provided by the user. Do not respond in any other way that isnt a direct translation.\n" +
    "The user is a beginner eager to learn Paiute. You have access to several tools:\n" + 
    "- **English word search:** Translate words and phrases from English to Paiute.\n" +
    "- **semantic search:** Given an English sentence, retrieve similar Paiute translations to provide context and improve accuracy.\n" + 
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
    ", ".join([f"{f}->{l}" for f, l in LENIS_MAP.items()]) + "\n"
)

rag_instruction_messages = json.loads((thisdir / "few_shot/RAG_instructions/RAG_instructions_messages.json").read_text())
rag_instruction_messages.insert(0, {"role": "system", "content": system_prompt_RAG_instructions})

# RAG pipeline translator ------------------------------------------------------------------------
system_prompt_RAG_pipeline = (
    "You are a language translator for the language known as Owen's Valley Paiute. \n" + 
    "You will answer a direct translation for a sentence provided by the user.\n" +
    "The user is a beginner eager to learn Paiute. You have access to several tools:\n" + 
    "- **Translation:** Translate words and phrases between English and Paiute.\n" +
    "- **Semantic Search:** Given an English sentence, retrieve similar Paiute translations to provide context and improve accuracy.\n" + 
    "- **split_stentence:** Given a complex english sentence (ex. I saw two men walking their dogs yesterday at Starbucks while drinking a cup of coffee), split it into simple sentences (Subject-Verb-Object (SVO) or Subject-Verb (SV) format) to make it easier to translate (I saw two men. The men were walking their dogs. The men were drinking coffee.).\n" +
    "- **Sentence Builder:** Use simple sentence translator function to help in developing the grammatically correct sentence in Paiute.\n"
)

RAG_pipeline_messages = json.loads((thisdir / "few_shot/RAG_pipeline/RAG_pipeline_messages.json").read_text())
RAG_pipeline_messages.insert(0, {"role": "system", "content": system_prompt_RAG_pipeline})


system_prompt_instructions_pipeline = (
    "You are a language translator for the language known as Owen's Valley Paiute. \n" + 
    "You will answer a direct translation for a sentence provided by the user.\n" +
    "The user is a beginner eager to learn Paiute translations. You have access to several tools:\n" + 
    "- **split_stentence:** Given a complex english sentence (ex. I saw two men walking their dogs yesterday at Starbucks while drinking a cup of coffee), split it into simple sentences (Subject-Verb-Object (SVO) or Subject-Verb (SV) format) to make it easier to translate (I saw two men. The men were walking their dogs. The men were drinking coffee.).\n" +
    "- **Simple sentence translator:** Use simple sentence translator function to help in developing the grammatically correct sentence in Paiute.\n" +
    "You can use the following grammar rules to check user input sentences from English to Owens Valley Paiute in addition to the other tools available to you.\n" + 
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
    ", ".join([f"{f}->{l}" for f, l in LENIS_MAP.items()]) + "\n"
)

instructions_pipeline = json.loads((thisdir / "few_shot/instructions_pipeline/instructions_pipeline_messages.json").read_text())
instructions_pipeline.insert(0, {"role": "system", "content": system_prompt_instructions_pipeline})