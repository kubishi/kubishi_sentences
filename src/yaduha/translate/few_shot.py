import json
import random
import pathlib
import argparse
import string
from pydantic import BaseModel

from yaduha.chatbot.tools.functions import search_english, search_sentences
from yaduha.translate.full_translator import translate_simple_sentences
from yaduha.translate.pipeline import split_sentence


thisdir = pathlib.Path(__file__).parent.absolute()

characters = string.ascii_letters + string.digits

model = "gpt-4o-mini"

def get_random_tool_call_id():
    """Generate a random tool call id of the form call_aSENunZCF31ob7zV89clvL4n"""
    return "call_" + ''.join(random.choices(characters, k=24))


def get_functions(path_input):
    print(path_input.name)
    if path_input.name == "full_translator.json" or path_input.name == "RAG_pipeline.json":
        return {
            "search_english": search_english,
            "search_sentences": search_sentences,
            "translate_simple_sentences": translate_simple_sentences,
            "split_sentence": split_sentence 
        }
    elif path_input.name == "instructions_pipeline.json":
        return {
            "translate_simple_sentences": translate_simple_sentences,
            "split_sentence": split_sentence 
        }
    elif path_input.name == "RAG_instructions.json":
        return {
            "search_sentences": search_sentences,
            "search_english": search_english
        }
    else:
        raise ValueError(f"input file not documented: {path_input}")

def main():
    
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Generate examples for the translator")
    parser.add_argument("input", help="Path to the examples file: Options: \n\nfull_translator.json, \n RAG_pipeline.json, \n instructions_pipeline.json, \n RAG_instructions.json")

    args = parser.parse_args()

    path_input = pathlib.Path(args.input).resolve()
    if not path_input.exists():
        raise FileNotFoundError(f"Input file {path_input} does not exist.")

    functions = get_functions(path_input)
    
    path_hydrated = path_input.parent / f"{path_input.stem}_hydrated.json"

    path_output = path_input.parent / f"{path_input.stem}_messages.json"

    examples = json.loads(path_input.read_text())
    prev_responses = {}
    if path_hydrated.exists():
        prev_responses = {
            example["query"]: example["response"]
            for example in json.loads(path_hydrated.read_text())
        }

    for example in examples:
        print(f"Query: {example['query']}")
        for tool_call in example.get("tool_calls", []):
            function = functions.get(tool_call["function"])

            result = None
            if function is split_sentence or function is translate_simple_sentences:
                result = function(sentence=tool_call["arguments"]["query"], model=model)
            else:
                result = function(**tool_call["arguments"])

            if isinstance(result, BaseModel):
                tool_call["result"] = json.dumps(result.model_dump(), ensure_ascii=False)
            else:
                tool_call["result"] = result

            tool_call["id"] = get_random_tool_call_id()
            print(f"Function: {tool_call['function']}")
            print(f"Arguments: {tool_call['arguments']}")
            print(f"Result: {tool_call['result']}")
            print()

        if "response" not in example:
            if example["query"] in prev_responses:
                example["response"] = prev_responses[example["query"]]
            else:
                example["response"] = input("Enter desired response: ")
        
        print(f"Response: {example['response']}")
        print()

    path_hydrated.write_text(json.dumps(examples, indent=2, ensure_ascii=False))

    #format as messages
    messages = []
    for example in examples:
        messages.append({
            "role": "user", 
            "content": example["query"]
        })

        tool_calls = [
            {
                "id": tool_call["id"],
                "function": {
                    "name": tool_call["function"],
                    "arguments": json.dumps(tool_call["arguments"])
                },
                "type": "function"
            }
            for tool_call in example.get("tool_calls", [])
        ]
        messages.append({
            "role": "assistant",
            "tool_calls": tool_calls
        })

        #add responses
        for tool_call in example.get("tool_calls", []):
            messages.append({
                "role": "tool",
                "content": json.dumps(tool_call["result"], ensure_ascii=False),
                "tool_call_id": tool_call["id"]
            })
        
        messages.append({
            "role": "assistant",
            "content": example["response"]
        })

    path_output.write_text(json.dumps(messages, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()