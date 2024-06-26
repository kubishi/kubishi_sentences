import argparse
from functools import lru_cache
import json
import logging
import os
import pathlib
import pprint
from typing import Callable, Optional

import dotenv
import openai
import pandas as pd

from sentence_builder import (NOUNS, Object, Subject, Verb, format_sentence,
                  get_random_sentence, sentence_to_str)

dotenv.load_dotenv()

thisdir = pathlib.Path(__file__).parent.absolute()

def get_english_structure(subject_noun: str,
                          subject_suffix: Optional[str],
                          verb: Optional[str],
                          verb_tense: Optional[str],
                          object_pronoun: Optional[str],
                          object_noun: Optional[str],
                          object_suffix: Optional[str]) -> str:
    sentence_details = []

    subject_info = {'part_of_speech': 'subject'}
    if subject_noun in NOUNS:
        subject_info['word'] = NOUNS[subject_noun]
        subject_info['positional'] = Subject.SUFFIXES[subject_suffix]
    elif subject_noun in Subject.PRONOUNS:
        subject_info['word'] = Subject.PRONOUNS[subject_noun]
    else: # unknown word
        subject_info['word'] = subject_noun
    sentence_details.append(subject_info)
    
    object_info = {'part_of_speech': 'object'}
    
    plural_keywords = ['plural', 'you all', 'they', 'them', 'we', 'us']
    if object_pronoun and any(kw in Object.PRONOUNS[object_pronoun] for kw in plural_keywords):
        object_info['plural'] = True
    if object_noun in NOUNS:
        object_info['word'] = NOUNS[object_noun]
        object_info['positional'] = Object.SUFFIXES[object_suffix]
        sentence_details.append(object_info)
    elif object_pronoun and not object_noun: # object pronoun
        object_info['word'] = Object.PRONOUNS[object_pronoun]
        sentence_details.append(object_info)
    elif (object_noun or '').strip(): # unknown word
        object_info['word'] = object_noun
        object_info['positional'] = Object.SUFFIXES[object_suffix]
        sentence_details.append(object_info)

    verb_info = {'part_of_speech': 'verb'}
    verb_info['word'] = Verb.TRANSIITIVE_VERBS.get(verb, Verb.INTRANSITIVE_VERBS.get(verb))
    if verb_info['word'] is None:
        # raise Exception(f"Invalid verb: {verb}")
        verb_info['word'] = verb
    verb_info['tense'] = Verb.TENSES[verb_tense]
    sentence_details.append(verb_info)

    return sentence_details

from openai.types.chat import ChatCompletion
# @lru_cache(maxsize=1000)
def translate(subject_noun: str,
              subject_suffix: Optional[str],
              verb: Optional[str],
              verb_tense: Optional[str],
              object_pronoun: Optional[str],
              object_noun: Optional[str],
              object_suffix: Optional[str],
              model = None,
              res_callback: Optional[Callable[[ChatCompletion], None]] = None) -> str:
    if model is None:
        model = os.environ['OPENAI_MODEL']
    structure = get_english_structure(
        subject_noun, subject_suffix,
        verb, verb_tense,
        object_pronoun, object_noun, object_suffix
    )

    examples = [
        {
            'role': 'user', 
            'content': json.dumps(
                [{'part_of_speech': 'subject', 'positional': 'proximal', 'word': 'wood'},
                {'part_of_speech': 'object', 'positional': 'proximal', 'word': 'dog'},
                {'part_of_speech': 'verb', 'tense': 'present ongoing (-ing)', 'word': 'see'}]
            )
        },
        {'role': 'assistant', 'content': 'This wood is seeing this dog.'},
        {
            'role': 'user',
            'content': json.dumps(
                [{'part_of_speech': 'subject', 'positional': 'proximal', 'word': 'cup'},
                 {'part_of_speech': 'object', 'positional': 'distal', 'word': 'cup', 'plural': True},
                 {'part_of_speech': 'verb', 'tense': 'future (will)', 'word': 'eat'}]
            )
        },
        {'role': 'assistant', 'content': 'This cup will eat those cups.'},
        {
            'role': 'user',
            'content': json.dumps(
                [{'part_of_speech': 'subject', 'positional': 'distal', 'word': 'pinenuts'},
                 {'part_of_speech': 'object', 'positional': 'distal', 'word': 'horse'},
                 {'part_of_speech': 'verb', 'tense': 'future (will)', 'word': 'see'}]
            )
        },
        {'role': 'assistant', 'content': 'Those pinenuts will see that horse.'},
    ]
    messages = [
        {'role': 'system', 'content': 'You are an assistant for translating structured sentences into simple natural English sentences.'},
        *examples,
        {'role': 'user', 'content': json.dumps(structure)}
    ]
    res = openai.chat.completions.create(
        model=model,
        messages=messages,
        timeout=10,
        temperature=0.0
    )
    if res_callback:
        res_callback(res)
    return res.choices[-1].message.content

def translate_random():
    choices = get_random_sentence()
    sentence_details = format_sentence(**{key: value['value'] for key, value in choices.items()})
    # print(sentence_details)
    print(f"Sentence: {sentence_to_str(sentence_details)}")
    translation = translate(**{key: value['value'] for key, value in choices.items()})
    print(f"Translation: {translation}")

def evaluate(num: int, savepath: pathlib.Path):
    rows = []
    if savepath.exists():
        df = pd.read_csv(savepath)
        rows = df.to_dict('records')
    for i in range(len(rows), num):
        print(f"Generating sentence {i+1}/{num}")
        choices = get_random_sentence()
        sentence_details = format_sentence(**{key: value['value'] for key, value in choices.items()})
        translation = translate(**{key: value['value'] for key, value in choices.items()})
        rows.append({
            'sentence': sentence_to_str(sentence_details),
            'translation': translation,
        })

        df = pd.DataFrame(rows)
        df.to_csv(savepath, index=False, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description='Translate OVP sentences to English')
    subparsers = parser.add_subparsers(dest='subparser_name')

    translate_parser = subparsers.add_parser('translate-random', help='Translate a randomly generated sentence')
    translate_parser.set_defaults(func='translate-random')

    evaluate_parser = subparsers.add_parser('evaluate', help='Evaluate the translation of a number of randomly generated sentences')
    evaluate_parser.add_argument('num', type=int, help='Number of sentences to evaluate')
    evaluate_parser.add_argument('savepath', type=pathlib.Path, help='Path to save the evaluation results')
    evaluate_parser.set_defaults(func='evaluate')
    
    args = parser.parse_args()
    if args.func is None:
        parser.print_help()
        return
    elif args.func == 'translate-random':
        translate_random()
    elif args.func == 'evaluate':
        evaluate(args.num, args.savepath)

if __name__ == '__main__':
    main()