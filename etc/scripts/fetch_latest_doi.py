import requests
import os

CONCEPT_DOI = "10.5281/zenodo.16361290"
ZENODO_API = "https://zenodo.org/api/records"
TOKEN = os.getenv("ZENODO_TOKEN")

params = {
    "q": f"conceptdoi:{CONCEPT_DOI}",
    "sort": "version",
    "size": 1,
    "access_token": TOKEN
}

r = requests.get(ZENODO_API, params=params)
r.raise_for_status()
latest_record = r.json()["hits"]["hits"][0]
print(latest_record["doi"])
