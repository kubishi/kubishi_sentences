import requests
from typing import Dict, List, Tuple, ClassVar

from yaduha.tools import Tool

def format_word(response_words: List) -> List:
    """
    Format the word response from the API into a string.
    """
    filtered = [
        {
            "paiute_translation": item["lexical_unit"],
            "english": item["senses"][0]["gloss"],
            "definition": item["senses"][0].get( "definition")
        } for item in response_words
    ]

    return filtered

class SearchEnglishTool(Tool):
    name: str = "search_english"
    description: str = "Search for English to Paiute translations."
    KUBISHI_API_URL: ClassVar[str] = "https://dictionary.kubishi.com/api"

    def __call__(self, query: str, limit: int = 3) -> List[Dict]:
        response = requests.get(f"{SearchEnglishTool.KUBISHI_API_URL}/search/english", params={"query": query, "limit": limit})
        response.raise_for_status()
        res_json: List[Dict] = response.json()

        results = [
            {
                "paiute_translation": item.get("lexical_unit"),
                "english": (item.get("senses") or [{}])[0].get("gloss"),
                "definition": (item.get("senses") or [{}])[0].get("definition")
            } for item in res_json
        ]

        return results
    
    def get_examples(self, examples: List[List[str]] = [["where", "is", "my", "dog"], ["Rock", "going to", "hit", "cat",]], limit: int = 3) -> List[Tuple[Dict, List[Dict]]]:
        """
        Get examples for the tool. 

        Args:
            words (List[List[str]]): Words to search for for each given prompt Default: [["where", "is", "my", "dog"], ["Rock", "going to", "hit", "cat",]].
            limit (int, optional): Limit the number of results. Defaults to 5.

        Returns:
            List[List[Tuple[Dict, List[Dict]]]]: A list of a list of tuples of (input, output), input has an index value indicating which index is part of the certain specific example
        """

        flat: List[Tuple[Dict, List[Dict]]] = []

        for i, group in enumerate(examples):
            for word in group:
                input = {"query": word, "limit": limit, "example_index": i}
                output = self(query=word, limit=limit)
                flat.append((input, output))

        return flat 
    
class SearchPaiuteTool(Tool):
    name: str = "search_paiute"
    description: str = "Search for Paiute to English translations."
    KUBISHI_API_URL: ClassVar[str] = "https://dictionary.kubishi.com/api"

    #TODO: Similar to search_english, filter only the necessary fields

    def __call__(self, query: str, limit: int = 3) -> List[Dict]:
        response = requests.get(f"{SearchPaiuteTool.KUBISHI_API_URL}/search/paiute", params={"query": query, "limit": limit})
        response.raise_for_status()
        res_json: List[Dict] = response.json()
        return format_word(res_json)
    
    def get_examples(self, words: List[str] = ["nüümü", "pöyö"], limit: int = 5) -> List[Tuple[Dict, List[Dict]]]:
        examples = [
            ({"query": word, "limit": limit}, self(query=word, limit=limit)) for word in words
        ]
        return examples

class SearchSentencesTool(Tool):
    name: str = "search_sentences"
    description: str = "Search for sentences in English (semantic search)."
    KUBISHI_API_URL: ClassVar[str] = "https://dictionary.kubishi.com/api"
    
    def __call__(self, query: str, limit: int = 3) -> List[Dict]:
        response = requests.get(f"{SearchPaiuteTool.KUBISHI_API_URL}/search/sentence", params={"query": query, "limit": limit})
        response.raise_for_status()
        res_json = response.json()
        infos = []
        for sentence in res_json:
            infos.append({
                "sentence": sentence["sentence"],
                "translation": sentence["translation"]
            })
        return infos
    
    def get_examples(self, sentences: List[str] = ["Where is my dog", "That rock is going to hit that cat"], limit: int = 5):
        examples = [
            ({"query": sentence, "limit": limit, "example_index": i}, self(query=sentence, limit=limit)) for i, sentence in enumerate(sentences)
        ]
        return examples