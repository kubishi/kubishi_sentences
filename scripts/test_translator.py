from yaduha.translators.builder import BuilderTranslator
from yaduha.translators.rag import RAGTranslator

def main():
    rag_translator = RAGTranslator()
    print(rag_translator("Hello, how are you?"))

if __name__ == "__main__":
    main()

