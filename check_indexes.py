# check_indexes.py
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv
import os

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")  # https://rag-chatbotrix-search.search.windows.net
key = os.getenv("AZURE_SEARCH_KEY")

client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))

print("Existing indexes on this Search resource:")
for index in client.list_indexes():
    print(f" - {index.name}")