# clear_test_reports.py
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
import os

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = "financial-reports-index"

search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(key))

# Step 1: List all documents currently in the index, so you can see what's there
print("Current documents in index:")
results = search_client.search(search_text="*", select=["id", "ticker", "date", "recommendation"])
ids_to_delete = []
for r in results:
    print(f" - id={r['id']}, ticker={r['ticker']}, date={r['date']}, recommendation={r['recommendation']}")
    ids_to_delete.append({"id": r["id"]})

# Step 2: Confirm before deleting
if ids_to_delete:
    confirm = input(f"\nDelete all {len(ids_to_delete)} document(s) shown above? (yes/no): ")
    if confirm.strip().lower() == "yes":
        result = search_client.delete_documents(documents=ids_to_delete)
        print(f"Deleted {len(result)} document(s).")
    else:
        print("Cancelled — no documents deleted.")
else:
    print("Index is already empty.")