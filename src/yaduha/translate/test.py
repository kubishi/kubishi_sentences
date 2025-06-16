from yaduha.translate.ablation.translation_functions import translate_sentence, split_sentence_tool, translate_simple_sentences
from yaduha.chatbot.tools.functions import search_english, search_sentences
from yaduha.translate.ablation.ablation_tools import rag_pipeline_messages, rag_tools, pipeline_tools

def main():

    functions = {
        "search_english": search_english,
        "search_sentences": search_sentences,
        "split_sentence": split_sentence_tool,
        "translate_simple_sentence": translate_simple_sentences
    }

    response = translate_sentence(sentence="The weasel swam", functions=functions, example_messages=rag_pipeline_messages, tools=rag_tools + pipeline_tools)

    print(response)


if __name__ == "__main__":
    main()