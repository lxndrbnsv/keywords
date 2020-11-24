import os
import json


domain_dirs = os.listdir(
    "./domain_data"
)

strings = []

for domain_dir in domain_dirs:
    files_list = os.listdir(
        f"./domain_data/{domain_dir}"
    )
    for file in files_list:
        file_path = f"./domain_data/{domain_dir}/{file}"

        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)

        query_stripped = json_data["query"].replace(
            " ", ""
        ).replace("-", "")
        if query_stripped not in strings:
            strings.append(query_stripped)
        else:
            os.remove(file_path)
