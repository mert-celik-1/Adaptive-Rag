from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    print("hello world")

    openai_key = os.getenv("OPENAI_API_KEY")
    langchain_key = os.getenv("LANGCHAIN_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    # Example usage
    print(f"OpenAI API Key exists: {bool(openai_key)}")
    print(f"LangChain API Key exists: {langchain_key}")
    print(f"Tavily API Key exists: {bool(tavily_key)}")