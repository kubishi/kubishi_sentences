import argparse
import json
from pathlib import Path

def load_results(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_results(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_missing_back_translation(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""  # empty string
    return False

def normalize_back_translation(text):
    text = text.strip()
    if not text:
        return text
    # Capitalize first word
    text = text[0].upper() + text[1:]
    # Add period if not already punctuated
    if text[-1] not in ".!?":
        text += "."
    return text

def prompt_for_missing_back_translations(data, path):
    results = data.get("results", [])
    for i, entry in enumerate(results):
        translation = entry.get("translation", {})
        back_translation = translation.get("back_translation", "")

        # Skip if back_translation is filled or marked as N/A
        if isinstance(back_translation, str) and back_translation.strip().lower() == "n/a":
            continue
        if not is_missing_back_translation(back_translation):
            continue

        source = translation.get("source", "[No source sentence]")
        target = translation.get("target", "[No target sentence]")
        print(f"\nEntry {i + 1}/{len(results)}")
        print(f"Source: {source}")
        print(f"Target: {target}")
        user_input = input("Enter back translation (or press Enter to skip): ").strip()
        if user_input:
            cleaned = normalize_back_translation(user_input)
            translation["back_translation"] = cleaned
            save_results(path, data)
            print(f"Saved: {cleaned}")
        else:
            print("Skipped.")

def main():
    parser = argparse.ArgumentParser(description="Fill in missing back translations (excluding 'N/A').")
    parser.add_argument("file", type=Path, help="Path to the JSON results file")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File '{args.file}' does not exist.")
        return

    data = load_results(args.file)
    prompt_for_missing_back_translations(data, args.file)

if __name__ == "__main__":
    main()
