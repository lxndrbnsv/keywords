import os
import json
import string
import random

sources = os.listdir("./storage/fetched_data")
for s in sources:
    files = os.listdir(f"./storage/fetched_data/{s}")
    for file in files:
        file_path = f"./storage/fetched_data/{s}/{file}"

        with open(file_path, "r") as json_file:
            json_source = json.load(json_file)

        for j in json_source["results"]:
            domain = j["website_link_text"]
            domain_dir_name = domain.replace(".", "_")
            print(domain, flush=True)

            data = {
                "query": json_source["query"],
                "ad": j
            }

            save_path = f"./storage/domain_data/{domain_dir_name}/"
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            charnum = 4
            letters = string.ascii_letters
            digits = string.digits
            file_name = "".join(random.choice(letters + digits) for __ in range(charnum))

            available_names = []
            for n in os.listdir(save_path):
                available_names.append(n.replace(".json", ""))

            while file_name in available_names:
                charnum = charnum + 1
                file_name = "".join(random.choice(letters + digits) for __ in range(charnum))

            result_data = json.dumps(data)
            with open(save_path + file_name + ".json", "w") as json_file:
                json_file.write(result_data)

