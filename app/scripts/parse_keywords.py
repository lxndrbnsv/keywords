import json

from app.models import KeywordsDomain


class GetDomains:
    def __init__(self, domain):
        def manage_site_links(site_links_all):
            """Возвращает данные быстрых ссылок в виде словаря."""
            if site_links_all != "null":
                max_len_texts = 8
                texts = []
                links = []
                for idx, sl in enumerate(site_links_all):
                    texts.append(sl["site_link_text"])
                    links.append(f"site.ru/{str(idx + 1)}")
                bars_to_add = (max_len_texts - len(texts)) * 2
                texts = "||".join(texts)
                links = "||".join(links)

                sl_data = {"texts": texts + "|" * bars_to_add, "links": links}

            else:
                sl_data = {
                    "texts": None,
                    "links": None,
                }
            return sl_data

        def manage_additional_info(additional_info):
            """Возвращает уточнения с разделителями."""
            if additional_info != "null":
                splitted = additional_info.split("·", 1)[0].strip().split(". ")
                return "||".join(splitted)
            else:
                return None

        ws_file_name = f"{domain.split('.', 1)[0]}.xlsx"
        results_data = []

        db_domains = KeywordsDomain.query.filter_by(kw_domain=domain).all()

        for res in db_domains:
            file_path = res.kw_file_path
            with open(file_path, "r") as json_file:
                data = json.load(json_file)

                # Сюда добавляем результаты для выбранного домена.
                processed_results_data = []
                for r in data["results"]:
                    if domain == r["website_link_text"]:
                        processed_results_data = r
                data["results"] = processed_results_data

                results_data.append(data)

                # Присваиваем идентификаторы.
                ad_id = 0
                for data in results_data:
                    ad_id = ad_id + 1
                    data["results"]["id"] = ad_id

                for d1 in results_data:
                    for d2 in reversed(results_data):
                        if (
                            d1["query"] != d2["query"]
                            and d1["results"]["header"]
                            == d2["results"]["header"]
                            and d1["results"]["product_link"]
                            == d2["results"]["product_link"]
                            and d1["results"]["description"]
                            == d2["results"]["description"]
                        ):
                            d1["results"]["id"] = d2["results"]["id"]

        self.results = results_data
