import time
from typing import Dict, List, Tuple, Any
from yaduha.translators import Translation, Translator
from yaduha.common import get_openai_client

class FinetunedTranslator(Translator):
    model: str = "gpt-4o-mini"
    tools: List = []
    name: str = "finetuned_translator"
    description: str = "Translate text to the target language using a finetuned model with few-shot examples."
    
    system_prompt: str = ( # Should this be default? like in the original repo?
        "You are a translator for translating text from English to OVP. "
        "For any word that does not have an equivalent in OVP, "
        "leave the word untranslated and place it inside brackets. "
    )
    examples: List[Tuple[str, str]] = [ # Should this be default? like in the original repo?
        ("The sleet climbs that rafter.", "[sleet]-uu [rafter]-noka u-dsibui-dü"),
        ("The pouch has smelled this ledge.", "[pouch]-uu [ledge]-neika a-gwana-pü"),
        ("The jackrabbit is eating the pinenuts.", "kamü-uu tüba-neika a-düka-ti")
    ]
        
    def get_messages(self) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]
        for (source, target) in self.examples:
            messages.append({
                "role": "user",
                "content": source
            })
            messages.append({
                "role": "assistant",
                "content": target
            })
        return messages

    def __call__(self, sentence: str) -> Translation:
        start_time = time.time()
        messages = self.get_messages()
        messages.append({
            "role": "user",
            "content": sentence
        })

        client = get_openai_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=messages, # I can't figure out this error
            temperature=0.0,
        )
        target = response.choices[0].message.content
        if target is None: #needed for strict typing mode
            raise ValueError("API returned empty response")
        translation_time = time.time() - start_time
        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0

        return Translation(
            source=sentence,
            target=target,
            back_translation=None,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            translation_time=translation_time,
            back_translation_prompt_tokens=0,
            back_translation_completion_tokens=0,
            back_translation_time=0.0
        )

    def get_examples(self) -> List[Tuple[Dict, Any]]:
        return []
