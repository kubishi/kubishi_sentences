from yaduha.bots import Bot
import openai
import dotenv
import os

from yaduha.tools.search import SearchEnglishTool, SearchPaiuteTool
from yaduha.translators.pipeline import PipelineTranslator

dotenv.load_dotenv(dotenv.find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def main():
    bot = Bot(
        client=openai.Client(api_key=OPENAI_API_KEY),
        model="gpt-4o",
        tools=[
            SearchEnglishTool(),
            SearchPaiuteTool(),
            PipelineTranslator()
        ],
    )
    bot.run_cli()

if __name__ == "__main__":
    main()