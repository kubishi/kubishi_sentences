from yaduha.translate.RAG_instructions import translate_sentence as translate_sentence_rag_instructions
from yaduha.translate.RAG_pipeline import translate_sentence as translate_sentence_rag_pipeline
from yaduha.translate.full_translator import translate_sentence as translate_sentence_full
from yaduha.translate.instructions_pipeline import translate_sentence as translate_sentence_instructions

def main():
    sentence = "Lets go to the market."

    sentence_translation_ri = translate_sentence_rag_instructions(sentence, model="gpt-4o-mini")

    print("Completion result RI: ", sentence_translation_ri["translation"])

    sentence_translation_rp= translate_sentence_rag_pipeline(sentence, model="gpt-4o-mini")

    print("Completion result RP: ", sentence_translation_rp["translation"])

    sentence_translation_full = translate_sentence_full(sentence, model="gpt-4o-mini")

    print("Completion result Full: ", sentence_translation_full["translation"])

    sentence_translation_ip = translate_sentence_instructions(sentence, model="gpt-4o-mini")

    print("Completion result IP: ", sentence_translation_ip["translation"])



if __name__ == "__main__":
    main()