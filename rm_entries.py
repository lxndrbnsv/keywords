import os
import json


queries = []
with open("./query_names.txt", "r") as text_file:
    queries_nl = text_file.readlines()
for qn in queries_nl:
    queries.append(qn.replace("\n", ""))

domain_dir_paths = os.listdir("./storage/domain_data")
for idx, domain_dir in enumerate(domain_dir_paths):
    print(str(idx + 1) + " of " + str(len(domain_dir_paths)), flush=True)
    domain_files = os.listdir(
        f"./storage/domain_data/{domain_dir}"
    )
    for results_file in domain_files:
        file_path = f"./storage/domain_data/{domain_dir}/{results_file}"
        with open(file_path,"r") as json_file:
            json_data = json.load(json_file)
        q = json_data["query"]
        if q in queries:
            os.remove(file_path)
            print("Removed!", flush=True)

