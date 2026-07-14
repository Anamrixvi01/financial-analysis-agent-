# create_memory_index.py
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
)
from dotenv import load_dotenv
import os

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")

client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SimpleField(name="ticker", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="date", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
    SearchableField(name="report_text", type=SearchFieldDataType.String),
    SimpleField(name="recommendation", type=SearchFieldDataType.String, filterable=True),
]

index = SearchIndex(name="financial-reports-index", fields=fields)

result = client.create_or_update_index(index)
print(f"Index created/updated: {result.name}")