import logging
import json
from openai import OpenAI
from pydantic import BaseModel

from yaduha.common import get_openai_client
from yaduha.translate.pipeline import split_sentence
from yaduha.translate.pipeline import translate_simple, order_sentence


client = get_openai_client()

def split_sentence_tool(sentence: str, model: str = "gpt-4o-mini"):
    return split_sentence(sentence=sentence, model=model)

def translate_simple_sentences(sentence: str, model: str = "gpt-4o-mini"):
    print("SENTENCE____________: ", sentence)
    simple_sentences = split_sentence(sentence=sentence, model=model)

    target_simple_sentences = []

    for sentence in simple_sentences.sentences:
        subject, verb, _object = translate_simple(sentence)
        target_simple_sentence = order_sentence(subject, verb, _object)
        target_simple_sentences.append(" ".join(map(str, target_simple_sentence)))
    
    target_simple_sentence_nl = ". ".join(target_simple_sentences) + '.'
    return target_simple_sentence_nl

def translate_sentence(sentence: str, model: str = "gpt-4o-mini", functions: dict = {}, example_messages: list = [], tools: list = []) -> dict:
    messages = [
        *example_messages,
        {
            "role": "user",
            "content": sentence
        }
    ]

    while True:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
            tools=tools,
        )

        messages.append(json.loads(completion.choices[0].message.model_dump_json()))

        if completion.choices[0].message.content:
            logging.info("Response: " + completion.choices[0].message.content)

        if not completion.choices[0].message.tool_calls:
            translation = completion.choices[0].message.content
            break
        
        for tool_call in completion.choices[0].message.tool_calls:
            kwargs = json.loads(tool_call.function.arguments)
            logging.info(f"Function: {tool_call.function.name}")

            print("TOOL CALL = ", tool_call.function.name)
            function = functions.get(tool_call.function.name)
            if not function:
                logging.error(f"Function {tool_call.function.name} not found.")
                continue

            # Calling the necessary tool functions 
            res = function(**kwargs)
            print("RESPONSE = ", res)

            # Converting pydantic models to dict
            if isinstance(res, BaseModel):
                res = res.model_dump()

            messages.append({
                "role": "tool",
                "content": json.dumps(res, ensure_ascii=False),
                "tool_call_id": tool_call.id
            })

    response = {
        "translation_prompt_tokens": completion.usage.prompt_tokens,
        "translation_completion_tokens": completion.usage.completion_tokens,
        "translation_total_tokens": completion.usage.total_tokens,
        "translation": translation,
        "messages": messages
    }

    return response