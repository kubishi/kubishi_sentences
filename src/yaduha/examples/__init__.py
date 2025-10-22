from yaduha.translators import Translator
from pathlib import Path
import json

SAVEPATH = "."
def create_translator_example(translator: Translator, savepath="."):
    """Prompts the user to act as the model and provide example translations.
    
    Args:
        translator (Translator): The translator to create examples for.
        savepath (Path): The path to save the examples to.
    """
    # user can either use one of the translator.tools or output the translation
    tools = {
        tool.name: tool for tool in translator.tools    
    }

    # Creating the example file
    example_path = Path(savepath) / f"{translator.name}_examples.json"
    example_path.parent.mkdir(parents=True, exist_ok=True)  # ensure folders exist

    example = []

    # Input sentence
    input_sentence = input("Enter an English sentence to translate: ")
    example.append({"role": "user", "content": input_sentence})

    tool_calls = []
    tool_call_results = []

    #loop for user to use tools
    while True:
        print(f"You can use the following tools: {', '.join(tools.keys())}")

        tool_choice = input("Enter the name of the tool to use (or 'done' to finish and provide the translation): ")

        # If user is finished with the tool calls, then append the tool calls to the example
        if tool_choice == "done":
            break
        
        # If use has a tool to use, then append it to the tool calls
        elif tool_choice in tools:
            tool = tools[tool_choice]
            id = tool.get_random_tool_call_id()

            schema = tool.get_tool_call_schema()

            print(f"Using tool: {tool.name}. Here is the tool's schema: \n{schema}\n\n. What is the tool input that you will add?")
            
            tool_input = input("Enter the tool argument: ")
            
            tool_result = {"id": id, "function": {"name": tool.name, "arguments": f"query: {tool_input}" }, "type": "function"}

            tool_calls.append(tool_result)
            tool_call_results.append({"role": "tool", "content": tool(tool_input), "tool_call_id": id})

        else:
            print("Invalid tool name. Please try again.")

    example.append({"role": "assistant", "content": [], "tool_calls": tool_calls})
    example.extend(tool_call_results)

    output = input("Enter the output of the example")

    example.append({"role": "assistant", "content": output})

    old_examples = []

    if example_path.exists():
        try:
            old_examples = json.loads(example_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old_examples = []

    old_examples.extend(example)

    new_examples = json.dumps(old_examples, ensure_ascii=False, indent=2) + "\n"
    print(new_examples)

    example_path.write_text(new_examples, encoding="utf-8")