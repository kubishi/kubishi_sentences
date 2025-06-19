from typing import Dict
import openai
import pathlib
import json
import dotenv
import os

dotenv.load_dotenv()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
thisdir = pathlib.Path(__file__).parent.resolve()

def get_comparator(source: str, target: str, back_translation: str) -> Dict[str, int]:
    examples = [
        ("They are climbing.", "mahuw̃a tsibui-ti.", "They are climbing.", "They are climbing."),
        ("They will travel.", "uhuw̃a [travel]-wei.", "They will travel.", "They will [VERB]."),
        ("Plants grow.", "[grow]-dü [plant]-uu.", "The plant grows", "The [SUBJECT] [VERB]s."),
        ("John read a book.", "book-neika john-ii ma-nia-ku.", "John read the book", "John read the [OBJECT]."),
        ("The dog ate soup.", "soup-neika dog-uu ma-düka-ku.", "The dog ate the soup", "The [SUBJECT] ate [OBJECT]."),
        ("I run", "nüü poyoha-dü.", "I run", "I run."),
        ("The cat is sleeping.", "cat-uu üwi-ti.", "The cat is sleeping", "The cat is sleeping."),
    ]
    messages = [
        {
            "role": "system",
            "content": (
                "You are a system that creates a comparator for translations that excludes the english vocabulary used in target translations. "
                "The source sentence is the original sentence in English, "
                "the target sentence is the translation in another language, "
                "and the back translation is the translation of the target sentence back to English. "
                "The comparator is meant to be the same as the back translation, but with all English words replaced by placeholders. "
                "Only replace the english words with a placeholder like [VERB], [SUBJECT], [OBJECT], etc. "
                "Leave the rest of the sentence intact. "
                "If the translation doesn't contain any english words, return the original back translation. "
            )
        }
    ]
    for source_sentence, target_sentence, back_translation_sentence, comparator in examples:
        messages.append({
            "role": "user",
            "content": f"Source: {source_sentence}\nTarget: {target_sentence}\nBack Translation: {back_translation_sentence}"
        })
        messages.append({
            "role": "assistant",
            "content": comparator
        })

    messages.append({
        "role": "user",
        "content": f"Source: {source}\nTarget: {target}\nBack Translation: {back_translation}"
    })
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.0,
    )
    comparator = response.choices[0].message.content.strip()
    return comparator

def main():
    path = thisdir / 'results/evaluation_results_evaluated.json'
    results = json.loads(path.read_text())
    total = len(results["results"])

    for i, result in enumerate(results["results"]):    
        print(f"[{i+1}/{total}] Evaluating {result['translation']['source']} -> {result['translation']['target']}")
        if result.get("comparator"):
            print(f"  Skipping: Already evaluated")
            continue
        if "back_translation" not in result["translation"]:
            print(f"  Skipping: No back translation")
            continue

        if result["translation"]["back_translation"] == "N/A":
            comparator = "N/A"
            print(f"  Skipping: Back translation is 'N/A'")
        else:
            print(f"  Computing Comparator: {result['translation']['source']} -> {result['translation']['target']}")
            comparator = get_comparator(
                source=result["translation"]["source"],
                target=result["translation"]["target"],
                back_translation=result["translation"]["back_translation"]
            )

            # print(f"  Result: {result['translation']['source']} -> {result['translation']['target']}")
            # print(f"  Comparator: {comparator}")
            # print()

        result["comparator"] = comparator
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()