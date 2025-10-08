from yaduha.translators.rag_translator import RAGTranslator

def main():
    translator_tool = RAGTranslator()
    print(translator_tool("Hello, how are you?"))

if __name__ == "__main__":
    main()

