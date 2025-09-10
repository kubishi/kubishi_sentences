from typing import Dict, List
import requests
import pathlib
import dotenv
from openai import OpenAI
import os
from tsiipa.translate.tools_syntax import ToolCallFunction

# from yaduha.chatbot.tools.grammar import search_grammar as _search_grammar

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

thisdir = pathlib.Path(__file__).parent.absolute()

KUBISHI_API_URL = "https://dictionary.kubishi.com/api"

#TOOLS -------------------------------------

search_english = ToolCallFunction(
    tool_name="search_english", 
    tool_description="Search for Paiute words in English (semantic search).", 
    arguments=[
        ToolCallArgument(
            name="query",
            type="string",
            description="The search term, either a word or a sentence."
        )
    )]
).create_function()

search_paiute = ToolCallFunction(
    tool_name="search_paiute", 
    tool_description="Search for English words in Paiute (semantic search).", 
    property_description="The search term, either a word or a sentence."
).create_function()

search_sentences = ToolCallFunction(
    tool_name="search_sentences", 
    tool_description="Search for sentences in English (semantic search).", 
    property_description="The search term, either a word or a sentence."
).create_function()


tools = [
    ToolCallFunction.create_function(search_english),
    ToolCallFunction.create_function(search_paiute),
    ToolCallFunction.create_function(search_sentences)
]

#Helpers -------------------------------------

def format_word(response_words: List) -> List:
    """
    Format the word response from the API into a string.
    """
    words = []
    for word in response_words:
        senses = []
        for sense in word["senses"]:
            sense_info = {}
            sense_info['gloss'] = sense.get("gloss")
            sense_info['definition'] = sense.get("definition")
            sense_info['examples'] = []
            if sense.get("examples"):
                for example in sense["examples"]:
                    sense_info['examples'].append({
                        "form": example["form"],
                        "translation": example["translation"]
                    })

            senses.append(sense_info)
        words.append({
            "lexical_unit": word["lexical_unit"],
            "senses": senses
        })
    
    return words



#Search English ------------------------------
def search_english(query):
    response = requests.get(f"{KUBISHI_API_URL}/search/english", params={"query": query})
    response.raise_for_status()
    res_json: Dict = response.json()
    return format_word(res_json)


#Search sentences ------------------------------

def search_sentences(query):
    response = requests.get(f"{KUBISHI_API_URL}/search/sentence", params={"query": query})
    response.raise_for_status()
    res_json = response.json()
    infos = []
    for sentence in res_json:
        infos.append({
            "sentence": sentence["sentence"],
            "translation": sentence["translation"]
        })
    return infos

#Search Paiute ------------------------------
def search_paiute(query):
    response = requests.get(f"{KUBISHI_API_URL}/search/paiute", params={"query": query})
    response.raise_for_status()
    res_json = response.json()
    return format_word(res_json)

# def search_grammar(query):
#     query_result = _search_grammar(
#         query=query,
#         limit=5
#     )
#     relevant_information = [match["metadata"]["text"] for match in query_result["matches"]]
#     return relevant_information

