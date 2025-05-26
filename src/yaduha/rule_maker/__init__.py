from openai import OpenAI
import json
from yaduha.common import get_openai_client

client = get_openai_client()

system_prompt = (
    "You are a linguist and AI prompt engineer with deep experience in creating interpretable translation systems. "
    "Your task is to analyze a JSON array containing dictionaries of aligned English–Paiute sentences. "
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

def main():
    # Load the aligned sentence pairs
    with open("yaduha/rule_maker/sentences.json", "r", encoding="utf-8") as f:
        sentence_data = json.load(f)

    # Add sentence data to the prompt
    user_message = (
        "Here is the JSON array of English–Paiute sentence pairs:\n\n"
        f"{json.dumps(sentence_data, indent=2)}"
    )

    # Call GPT with chat model
    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4" if preferred
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
    )

    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()