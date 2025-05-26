from yaduha.translate.full_translator import translate_simple_sentences, translate_sentence


def main():
    sentence = "Where is my dog?"

    sentence_translation = translate_sentence(sentence, model="gpt-4o-mini")


if __name__ == "__main__":
    main()