"""
test_connection.py — Quick Azure OpenAI connection test

Run this FIRST to make sure your .env is correct before building any agents.
Usage: python test_connection.py

Expected output:
  ✅ Azure OpenAI connected!
  Response: Hello! I'm ready to help with financial analysis.
"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

def test_azure_openai_connection():
    print("Testing Azure OpenAI connection...")

    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )

    response = llm.invoke([
        HumanMessage(content="Say: 'Hello! I'm ready to help with financial analysis.'")
    ])

    print("✅ Azure OpenAI connected!")
    print(f"Response: {response.content}")

if __name__ == "__main__":
    test_azure_openai_connection()
