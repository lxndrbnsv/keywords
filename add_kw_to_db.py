import os
import json

from app import db
from app.models import KeywordsDomain


json_files = []  # Список json-файлов с результатами поиска.
existing = []  # Список уже проиндексированных файлов.


for k in KeywordsDomain.query.all():
    existing.append(k.kw_file_path)

results_folders = os.listdir("./storage/fetched_data")

for folder in results_folders:
    results_files = os.listdir(f"./storage/fetched_data/{folder}")
    for file in results_files:
        file_path = f"./storage/fetched_data/{folder}/{file}"
        if file_path not in existing:
            json_files.append(file_path)

for idx, file in enumerate(json_files):
    print(idx)
    with open(file, "r") as json_data:
        results_data = json.load(json_data)
        query = results_data["query"]
        for r in results_data["results"]:
            domain = r["website_link_text"]
            result_path = file

            domain_db = KeywordsDomain()
            domain_db.kw_domain = domain
            domain_db.kw_query = query
            domain_db.kw_file_path = result_path

            db.session.add(domain_db)
            db.session.commit()
