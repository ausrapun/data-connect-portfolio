import requests
from datetime import datetime, timezone
import json
import pandas as pd

# provided in notion settings (admin may be req)
token = 'your_token'
databaseID = "your_database_id"

headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "YOUR_NOTION_VERSION"
}

# get pages from databases
def get_pages(num_pages=None):
    url = f"https://api.notion.com/v1/databases/{databaseID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages
    
    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()  
        
    json_results = data["results"]

    return json_results

# results
results = get_pages()
data = []

# loop through results here 

# Create a DataFrame from the extracted data
df = pd.DataFrame(data)