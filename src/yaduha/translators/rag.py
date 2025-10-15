from collections import defaultdict
import json
import time
from typing import Dict, List, Tuple, Optional, Any
# from pydantic import Json
from yaduha.translators import Translator, Translation
from yaduha.tools import Tool
from yaduha.common import get_openai_client
from yaduha.tools.search import SearchEnglishTool, SearchSentencesTool
from yaduha.bots import Bot


class RAGTranslator(Translator):
    model: str = "gpt-4o-mini"
    tools: List[Tool] = [SearchEnglishTool(), SearchSentencesTool()]
    name: str = "rag_translator"
    description: str = "Translate text to the target language using retrieval-augmented generation (RAG) with a set of tools."
    
    # System messages for translation context
    prompt: str =(
        "You are a language translator for the language known as Owen's Valley Paiute. \n"
        "You will answer a direct translation for a sentence provided by the user.\n"
        "The user is a beginner eager to learn Paiute translations. You have access to several tools:\n"
        "- **English word search:** Translate words and phrases from English to Paiute.\n"
        "- **semantic search:** Given an English sentence, retrieve similar Paiute translations to provide context and improve accuracy.\n"
        "You can use the following grammar rules to check user input sentences from English to Owens Valley Paiute in addition to the other tools available to you.\n"
        "Use the vocabulary and sentence structures available to translate the input sentence as best as possible.\n"
        "It doesn't need to be perfect and you can leave English words untranslated if necessary.\n"
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
    
    
    
    def create_few_shot(self) -> None:

        sentence_examples = ["Where is the dog", "That rock is going to hit that cat"]
        sentence_example_results = ["Hanno 'i-doogü'?", "tübbi-uu kidi'-oka u-gwati-gaa-wei"]

        messages = [
            {"role": "system", "content": self.prompt},
        ]

        tool_calls = {tool.name: [] for tool in self.tools}

        for tool in self.tools:
            examples = tool.get_examples()

            # Group tool calls by their example index
            #It is a list[list[tuple[input, output]]]
            grouped_examples = defaultdict(list)
            for pair in examples:
                sentence_index = pair[0]["example_index"]
                grouped_examples[sentence_index].append(pair)
                
            grouped_examples = list(grouped_examples.values())

            # for i, group in enumerate(grouped_examples):
            #     print(f"Sentence {i}:")
            #     for item in group:
            #         print("  ", item)

            # Iterating over every example
            for example in grouped_examples:
                example_tool_calls = []
                example_tool_call_outputs = []

                for input_example, output_example in example:
                    tool_id = tool.get_random_tool_call_id()
                    query = json.dumps({"query": input_example['query']})

                    example_tool_calls.append({
                        "id": tool_id, 
                        "function": {
                            "name": tool.name, 
                            "arguments": query
                        },
                        "type": "function"
                    })

                    example_tool_call_outputs.append({
                        "role": "tool",
                        "content": output_example,
                        "tool_call_id": tool_id
                    })
                
                # Every tool call is its own key and each key is a list of examples, where each example is a tuple pair of the tool call input and the response output. 
                #Not sure if there is an easier way to do this, but this was the best I could come up with
                tool_calls[tool.name].append((example_tool_calls, example_tool_call_outputs))
            
        print("TOOL CALLS", tool_calls, "\n\n")

        # Appending everything into one json object
        for i, sentence_example in enumerate(sentence_examples):
            # Appending what the message translation needs to be
            messages.append({"role": "user", "content": sentence_example})

            # Appending the tool calls that the user will make
            input_tool_calls = []
            output_tool_calls = []

            for tool_name in tool_calls:
                input_tool_calls.extend(tool_calls[tool_name][i][0])
                output_tool_calls.extend(tool_calls[tool_name][i][1])

            messages.append({"role": "assitant", "tool_calls": json.dumps(input_tool_calls)})

            messages.extend(output_tool_calls)

            messages.append({"role": "assistant", "content": sentence_example_results[i]})
            
            
        return json.dumps(messages)

