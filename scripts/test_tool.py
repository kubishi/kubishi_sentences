from yaduha.tools.search import SearchEnglishTool


def main():
    search_english_tool = SearchEnglishTool()
    print(SearchEnglishTool.model_json_schema())
    print(search_english_tool.get_tool_call_schema())

    response = search_english_tool(query="dog", limit=3)
    print(response)

if __name__ == "__main__":
    main()