import requests
from typing import Dict, List, Tuple, ClassVar

from yaduha.tools import Tool

class SearchEnglishTool(Tool):
    name: str = "search_english"
    description: str = "Search for English to Paiute translations."
    KUBISHI_API_URL: ClassVar[str] = "https://dictionary.kubishi.com/api"

    def __call__(self, query: str, limit: int) -> List[Dict]:
        response = requests.get(f"{SearchEnglishTool.KUBISHI_API_URL}/search/english", params={"query": query})
        response.raise_for_status()
        res_json: List[Dict] = response.json()
        return res_json
    
    def get_examples(self, words: List[str] = ["hello", "water"], limit: int = 5) -> List[Tuple[Dict, List[Dict]]]:
        examples = [
            ({"query": word, "limit": limit}, self(query=word, limit=limit)) for word in words
        ]
        return examples
    
class SearchPaiuteTool(Tool):
    name: str = "search_paiute"
    description: str = "Search for Paiute to English translations."
    KUBISHI_API_URL: ClassVar[str] = "https://dictionary.kubishi.com/api"

    def __call__(self, query: str, limit: int) -> List[Dict]:
        response = requests.get(f"{SearchPaiuteTool.KUBISHI_API_URL}/search/paiute", params={"query": query})
        response.raise_for_status()
        res_json: List[Dict] = response.json()
        return res_json
    
    def get_examples(self, words: List[str] = ["nüümü", "pöyö"], limit: int = 5) -> List[Tuple[Dict, List[Dict]]]:
        examples = [
            ({"query": word, "limit": limit}, self(query=word, limit=limit)) for word in words
        ]
        return examples
