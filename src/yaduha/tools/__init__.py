import logging
from pydantic import BaseModel, create_model
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from abc import abstractmethod
import random
import string
import inspect
import jsonschema

from openai.types.responses import FunctionToolParam


class Tool(BaseModel):
    name: str
    description: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.name.isidentifier():
            raise ValueError(f"Tool name '{self.name}' is not a valid Python identifier.")
        if self.name in {"print", "input", "len", "str", "int", "float", "list", "dict", "set", "tuple"}:
            raise ValueError(f"Tool name '{self.name}' is a reserved Python keyword or built-in function name.")
        self.validate_examples()

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    @staticmethod
    def get_random_tool_call_id():
        """Generate a random tool call id of the form call_aSENunZCF31ob7zV89clvL4n"""
        return "call_" + ''.join(random.choices(string.ascii_letters + string.digits, k=24))

    def get_tool_call_schema(self) -> FunctionToolParam:
        signature = inspect.signature(self.__call__)
        properties = {}
        for name, param in signature.parameters.items():
            if name == "self":
                continue
            annotation = param.annotation
            if annotation == inspect._empty:
                annotation = Any
            default = param.default
            if default == inspect._empty:
                default = ...
            properties[name] = (annotation, default)

        model = create_model(self.name, **properties)
        schema = FunctionToolParam(
            name=self.name,
            parameters=model.model_json_schema(),
            strict=False,
            type="function",
            description=self.description,
        )
        return schema
    
    def get_tool_call_output_schema(self) -> Dict:
        signature = inspect.signature(self.__call__)
        return_type = signature.return_annotation
        if return_type == inspect._empty:
            return_type = Any
        model = create_model(f"{self.name}_output", output=(return_type, ...))
        schema = model.model_json_schema()
        return schema
    
    @abstractmethod
    def get_examples(self, *args, **kwargs) -> List[Tuple[Dict, Any]]:
        """Get examples for the tool. 

        Args:
            *args: Extra arguments to customize the examples.
            **kwargs: Extra keyword arguments to customize the examples.

        Returns:
            List[Tuple[Dict, Dict]]: A list of tuples of (input, output)
        """
        raise NotImplementedError
    
    def validate_examples(self) -> None:
        """Validate the examples for the tool."""
        examples = self.get_examples()
        schema = self.get_tool_call_schema()
        output_schema = self.get_tool_call_output_schema()
        
        for i, (input_example, output_example) in enumerate(examples):
            try:
                jsonschema.validate(instance=input_example, schema=schema["parameters"] or {})
            except jsonschema.ValidationError as e:
                raise ValueError(f"Example {i} input does not conform to schema: {e.message}")
            try:
                jsonschema.validate(instance={"output": output_example}, schema=output_schema) 
            except jsonschema.ValidationError as e:
                raise ValueError(f"Example {i} output does not conform to schema: {e.message}")
            
        logging.debug(f"All {len(examples)} examples are valid for tool {self.name}.")

