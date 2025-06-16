import json
import pathlib

from yaduha.common import get_openai_client
from yaduha.chatbot.tools.functions import search_english, search_sentences

client = get_openai_client()

thisdir = pathlib.Path(__file__).parent.absolute()

functions = {
    "search_english": search_english,
    "search_sentences": search_sentences
}

#TOOLS -------------------------------------
tools = [
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

    #Search Sentences ----------------------------
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


system_prompt = (
    "You are a linguist and AI prompt engineer with deep experience in creating interpretable translation systems. "
    "Your task is to analyze a JSON array containing dictionaries of aligned English–Paiute sentences. "
    "If you need to translate sentences further, you may use the tools provided to search for words and sentences to provide the best translation possible."
    "Based on these pairs, write a **detailed and systematic set of translation rules** that a human or AI could follow to translate new English sentences into Paiute. Focus on extracting grammatical patterns such as:\n\n"
    "- Subject object verb order (SOV, SVO, etc.)\n"
    "- Word-by-word or morpheme-by-morpheme mappings\n"
    "- Affixes (prefixes/suffixes)\n"
    "- Markers for tense, plurality, gender, possession, etc.\n"
    "- Irregular constructions or exceptions\n"
    "- Word order rules\n"
    "- Any idiomatic or cultural context\n\n"
    "**Instructions:**\n"
    "1. Start by summarizing any observable linguistic patterns.\n"
    "2. Then present translation rules step-by-step.\n"
    "3. Include multiple examples and edge cases to illustrate the rules.\n"
    "Please respond with clearly structured sections:\n"
    "- **1. Pattern Summary**\n"
    "- **2. Translation Rules**\n"
    "- **3. Example Applications**\n"
)

example_messages = json.loads((thisdir / "example_messages.json").read_text())

def main():
    # Load the aligned sentence pairs
    with open(thisdir / "sentences.json", "r", encoding="utf-8") as f:
        sentence_data = json.load(f)

    # Add sentence data to the prompt
    user_message = (
        "Here is the JSON array of English–Paiute sentence pairs:\n\n"
        f"{json.dumps(sentence_data, indent=2)}"
    )

    messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

    # Call GPT with chat model
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4" if preferred
        messages=messages,
        temperature=0.0,
    )

    messages.append(response.choices[0].message)
    print(response.choices[0].message.content)

    messages.extend(example_messages)

    while True:


        user_message = input("You: ")
        messages.append({"role": "user", "content": user_message})
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4" if preferred
            messages=messages,
            tools=tools,
            temperature=0.0,
        )

        res = response.choices[0].message
        messages.append(res)

        if res.tool_calls:
            for tool_call in res.tool_calls:
                print(tool_call.function)
                tool_name = tool_call.function.name
                kwargs = json.loads(tool_call.function.arguments)

                tool_func = functions.get(tool_name)
                if not tool_func:
                    print(f"Unknown tool: {tool_name}")
                    continue
                
                tool_result = tool_func(**kwargs)

                # If result is pydantic model, dump to dict
                if hasattr(tool_result, "model_dump"):
                    tool_result = tool_result.model_dump()

                messages.append({
                    "role": "tool", 
                    "tool_call_id": tool_call.id, 
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  
                messages=messages,
                tools=tools,
                temperature=0.0,
            )

            res = response.choices[0].message
            messages.append(res)
            print(res.content)

        elif res.content:
            print("res.content: ", res.content)
            continue

        else:
            print("No content and no tool calls in response: " + res)
            break

        

if __name__ == "__main__":
    main()