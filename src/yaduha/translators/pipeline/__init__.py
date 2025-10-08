import time
from openai.types.chat import ChatCompletion

from yaduha.translators import Translator, Translation
from yaduha.tools import Tool

# pipeline modules
from yaduha.translators.pipeline.pipeline_functions import split_sentence, comparator_sentence, translate_simple, order_sentence, make_sentence
from yaduha.translators.pipeline.pipeline_syntax import SentenceList
from yaduha.translators.pipeline.pipeline_back_translate import translate as translate_ovp_to_english
from typing import Dict, List, Tuple


class PipelineTranslator(Translator):
    tools: List[Tool] = []
    name: str = "pipeline_translator"
    description: str = "Translate text to the target language and back to the source language using a pipeline of tools."
    model: str = "gpt-4o"

    def __call__(self, sentence: str) -> Translation:
        start_time = time.time()
        prompt_tokens = 0
        completion_tokens = 0
        model_calls = 0
        def res_callback(res: ChatCompletion):
            nonlocal prompt_tokens, completion_tokens, model_calls
            if res.usage is not None:
                prompt_tokens += res.usage.prompt_tokens
                completion_tokens += res.usage.completion_tokens
            model_calls += 1

        prompt_tokens_back = 0
        completion_tokens_back = 0
        model_calls_back = 0
        def res_callback_backwards(res: ChatCompletion):
            nonlocal prompt_tokens_back, completion_tokens_back, model_calls_back
            if res.usage is not None:
                prompt_tokens_back += res.usage.prompt_tokens
                completion_tokens_back += res.usage.completion_tokens
            model_calls_back += 1

        simple_sentences = split_sentence(sentence, model=self.model, res_callback=res_callback)
        comparator_sentences = []
        target_simple_sentences = []
        backwards_translations = []
        back_translation_time = 0
        for simple_sentence in simple_sentences.sentences:
            comparator_sentences.append(comparator_sentence(simple_sentence))
            subject, verb, _object = translate_simple(simple_sentence)
            target_simple_sentence = order_sentence(subject, verb, _object)
            target_simple_sentences.append(" ".join(map(str, target_simple_sentence)))
            back_translation_start_time = time.time()
            backwards_translations.append(
                translate_ovp_to_english(
                    subject_noun=subject.noun,
                    subject_noun_nominalizer=subject.subject_noun_nominalizer,
                    subject_suffix=subject.subject_suffix,
                    subject_possessive_pronoun=subject.possessive_pronoun,
                    verb=verb.verb_stem,
                    verb_tense=verb.tense_suffix,
                    object_pronoun=verb.object_pronoun_prefix,
                    object_noun=_object.noun if _object else None,
                    object_noun_nominalizer=_object.object_noun_nominalizer if _object else None,
                    object_suffix=_object.object_suffix if _object else None,
                    object_possessive_pronoun=_object.possessive_pronoun if _object else None,
                    res_callback=res_callback_backwards
                ).strip(".")
            )
            back_translation_time += time.time() - back_translation_start_time

        # simple_sentences_nl = ". ".join([make_sentence(sentence, model=self.model, res_callback=res_callback) for sentence in simple_sentences]) + '.'
        simple_sentences_nl = make_sentence(simple_sentences, model=self.model, res_callback=res_callback)
        comparator_sentence_nl = make_sentence(SentenceList(sentences=comparator_sentences), model=self.model, res_callback=res_callback_backwards)
        target_simple_sentence_nl = ". ".join(target_simple_sentences) + '.'
        backwards_translation_nl = ". ".join(backwards_translations) + '.'

        translation_time = (time.time() - start_time) - back_translation_time
        return Translation(
            source=sentence,
            target=target_simple_sentence_nl,
            back_translation=backwards_translation_nl,
            translation_prompt_tokens=prompt_tokens,
            translation_completion_tokens=completion_tokens,
            translation_time=translation_time,
            back_translation_prompt_tokens=prompt_tokens_back,
            back_translation_completion_tokens=completion_tokens_back,
            back_translation_time=back_translation_time,
            metadata={
                'simple': simple_sentences_nl,
                'comparator': comparator_sentence_nl,
                'model_calls': model_calls,
                'back_model_calls': model_calls_back,
            }
        )
    
    def get_examples(self, sentences: List[str] = ["I drink water"]) -> List[Tuple[Dict, Translation]]:
        examples = [
            ({"sentence": sentence}, self(sentence=sentence)) for sentence in sentences
        ]
        return examples