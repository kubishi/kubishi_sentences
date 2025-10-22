from yaduha.examples import create_translator_example
from yaduha.translators.rag import RAGTranslator


def main():
    create_translator_example(translator=RAGTranslator())

if __name__ == "__main__":
    main()