from . import Translator
from pathlib import Path
import json

def create_translator_example(translator: Translator, savepath: Path):
    """Prompts the user to act as the model and provide example translations.
    
    Args:
        translator (Translator): The translator to create examples for.
        savepath (Path): The path to save the examples to.
    """

    input_sentence = input("Enter an English sentence to translate: ")

    # user can either use one of the translator.tools or output the translation
    tools = {
        tool.name: tool for tool in translator.tools    
    }
    while True:
        tool_str = ", ".join(tools.keys())
        print(f"You can use the following tools: {tool_str}")
        tool_choice = input("Enter the name of the tool to use (or 'done' to finish and provide the translation): ")
        if tool_choice == "done":
            break
        elif tool_choice in tools:
            tool = tools[tool_choice]
            schema = tool.get_tool_call_schema()
            # TODO: based on schema, ask the user for the tool inputs
            inputs = {}
            result = tool(**inputs)
            print(f"Tool result: {result}")
        else:
            print("Invalid tool name. Please try again.")

    