from yaduha.translators.builder import BuilderTranslator

def main():
    translator_tool = BuilderTranslator(model="")
    print(translator_tool("Hello, how are you?"))

if __name__ == "__main__":
    main()

