from yaduha.tools.search import SearchEnglishTool, SearchSentencesTool
from yaduha.translators.pipeline import PipelineTranslator
from yaduha.translators.rag import RAGTranslator


def main():
    # search_english_tool = SearchEnglishTool()
    # print("\n\nEXAMPLES", search_english_tool.get_examples())

    # response_english = search_english_tool(query="dog", limit=3)
    # print(response_english)

    # search_sentences_tool = SearchSentencesTool()
    # print("\n\nMODEL SCHEMA", SearchSentencesTool.model_json_schema())
    # print("\n\nTOOL SCHEMA", search_sentences_tool.get_tool_call_schema())
    # print("\n\nEXAMPLES", search_sentences_tool.get_examples())

    # response_sentences = search_sentences_tool(query="I drink water", limit=3)
    # print(response_sentences)

    print("\n\n")

    # pipeline_tool = PipelineTranslator()
    # print(pipeline_tool.model_json_schema())
    # print(pipeline_tool.get_tool_call_schema())

    # response = pipeline_tool(sentence="I drink water")
    # print(response)

    rag = RAGTranslator()
    print(rag.create_few_shot())


if __name__ == "__main__":
    main()