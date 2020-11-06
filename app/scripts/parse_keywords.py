import os
import json

from app.models import KeywordsDomain


class GetDomains:
    def __init__(self, domain):
        ws_file_name = f"{domain.split('.', 1)[0]}.xlsx"
        results_data = []
        
        files_path = f"./storage/domain_data/{domain.replace('.', '_')}/"
        files = os.listdir(files_path)
        for f in files:
            file_path = files_path + f
            try:
                with open(file_path, "r") as json_file:
                    data = json.load(json_file)
                    results_data.append(data)
            except FileNotFoundError:
                pass

        self.results = results_data
