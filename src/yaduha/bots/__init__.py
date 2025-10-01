from copy import copy
import json
from typing import Dict, List
from pydantic import BaseModel
from abc import ABC, abstractmethod
from yaduha.tools import Tool


import openai


class Bot(ABC):
    def __init__(self,
                 client: openai.Client,
                 model: str,
                 tools: List[Tool],
                 name: str = "bot",
                 description: str = "A bot that can use tools to perform tasks."):
        self.client = client
        self.model = model
        self.tools = tools
        self.name = name
        self.description = description

    def __call__(self, messages: List) -> str:
        tools = {
            tool.name: tool for tool in self.tools
        }
        
        continue_calling = True
        while True:
            print([tool.get_tool_call_schema() for tool in self.tools])
            response = self.client.responses.create(
                model=self.model,
                input=messages,
                tools=[tool.get_tool_call_schema() for tool in self.tools],
                tool_choice="auto",
            )
            messages += response.output  
            continue_calling = False  
            for item in response.output:
                if item.type == "function_call":
                    continue_calling = True
                    tool = tools[item.name]
                    tool_response = tool(**json.loads(item.arguments))
                    messages.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(tool_response)
                    })

            if not continue_calling:
                return response.output_text

    def run_cli(self):
        print(f"Welcome to {self.name}!")
        print(self.description)
        print("Type 'exit' to quit.")
        messages = []
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            messages.append({"role": "user", "content": user_input})
            response = self(messages=messages)
            print(f"{self.name}: {response}")
            
    

