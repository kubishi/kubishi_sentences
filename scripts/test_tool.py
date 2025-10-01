from yaduha.tools.search import SearchEnglishTool
from yaduha.tools.pipeline import PipelineTranslate


def main():
    search_english_tool = SearchEnglishTool()
    print(SearchEnglishTool.model_json_schema())
    print(search_english_tool.get_tool_call_schema())

    response = search_english_tool(query="dog", limit=3)
    print(response)

    print("\n\n")

    pipeline_tool = PipelineTranslate()
    print(pipeline_tool.model_json_schema())
    print(pipeline_tool.get_tool_call_schema())

    response = pipeline_tool(query="I drink water")
    print(response)


if __name__ == "__main__":
    main()