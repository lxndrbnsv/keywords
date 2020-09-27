import os
import json
import idna
from multiprocessing import Pool
from idna import IDNAError
from idna.core import InvalidCodepoint

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ChunkedEncodingError


city_id = "213"
files = os.listdir("./small_files/filtered")


def parser(file):
    def get_search_results():
        """Возвращает список ссылок, собранных из выдачи поиска по
        Яндекс-директ, в виде html-кода."""
        try:
            direct_results_html = []

            # Выполняем поиск по объявлениям.
            pages = [
                "https://yandex.ru/search/direct?text="
                + query
                + "&lr="
                + city_id
            ]

            for page in pages:
                page_html = requests.get(page)
                page_bs = BeautifulSoup(page_html.text, "html.parser")

                for li in page_bs.find_all("li", {"class": "serp-item"}):
                    direct_results_html.append(li)

            return direct_results_html
        except ChunkedEncodingError:
            return None

    def get_header():
        try:
            head = link.find("h2").get_text()
        except AttributeError:
            head = None

        # Слэш в конце текста объявления означает, что второй заголовок
        # отсутствует. Поэтому первым делом происходит проверка на отутствие
        # второго заголовка и, в случае, если его нет, возвращаем заголовок.
        # Таким образом удается избежать деления строк, не имеющих второго
        # заголовка, но имеющих при этом тире или дефис.
        if " / " in head:
            head = link.find("h2").get_text().split(" / ", 1)[0].strip()
            return head
        if " - " in head:  # Дефис.
            head = link.find("h2").get_text().split(" - ", 1)[0].strip()
        if "–" in head:
            head = link.find("h2").get_text().split("–", 1)[0].strip()  # Тире.

        return head

    def get_second_header():
        """Возвращает второй заголовок."""
        try:
            try:
                # Внутри split() дефис.
                return link.find("h2").get_text().split(" - ", 1)[1].strip()
            except IndexError:
                # Внутри split() используется тире (U+2013), а не дефис.
                return link.find("h2").get_text().split("–", 1)[1].strip()
        except IndexError:
            return None
        except AttributeError:
            return None

    def get_site_links():
        """Быстрые ссылки. ОТОБРАЖАТЬ НЕ БУДЕМ."""
        s_links = []
        try:
            for a in link.find("div", {"class": "sitelinks"}).find_all("a"):
                s_links.append(a.attrs["href"])
        except AttributeError:
            return None
        if len(s_links) == 0:
            return None
        return s_links

    def get_site_links_text():
        sl_descriptions = []
        try:
            for a in link.find("div", {"class": "sitelinks"}).find_all("a"):
                sl_descriptions.append(a.get_text())
        except AttributeError:
            sl_descriptions = None
        if len(sl_descriptions) == 0:
            sl_descriptions = None
        return sl_descriptions

    def get_site_links_description():
        sl_desc = []
        try:
            for div in link.find_all("div", {"class": "sitelinks__desc"}):
                sl_desc.append(div.get_text())
        except AttributeError:
            pass

        if len(sl_desc) == 0:
            sl_desc = None

        return sl_desc

    def get_website_link():
        """Возвращает ссылку на главную страницу сайта."""
        try:
            # Для доменов в зоне рф конвертируем из idna.
            return "https://" + str(
                idna.decode(
                    link.find("div", {"class": "path"}).find("b").get_text()
                )
            )
        except InvalidCodepoint:
            return (
                "https://"
                + link.find("div", {"class": "path"}).find("b").get_text()
            )
        except IDNAError:
            return (
                "https://"
                + link.find("div", {"class": "path"}).find("b").get_text()
            )

    def get_website_link_text():
        try:
            return str(
                idna.decode(
                    link.find("div", {"class": "path"}).find("b").get_text()
                )
            )
        except InvalidCodepoint:
            return link.find("div", {"class": "path"}).find("b").get_text()
        except IDNAError:
            return link.find("div", {"class": "path"}).find("b").get_text()

    def get_product_link():
        try:
            return (
                link.find("div", {"class": "path"})
                .find("a")
                .find("span")
                .next_sibling
            )
        except AttributeError:
            return None

    def get_link():
        """Ссылка из h2."""
        return link.find("h2").find("a").attrs["href"]

    def get_description():
        """Возвращает описания. Без уточнений."""
        try:
            # Сначала выполняем поиск по элементу, в котором содержится
            # развернутое описание. Это позволяет избежать дублирования
            # текста.
            return (
                link.find("div", {"class": "text-container"})
                .find("span", {"class": "extended-text__full"})
                .get_text()
                .split("·", 1)[0]
                .replace("Скрыть", "")
                .strip()
            )
        except AttributeError:
            return (
                link.find("div", {"class": "text-container"})
                .get_text()
                .split("·", 1)[0]
                .strip()
            )
        except IndexError:
            try:
                return (
                    link.find("div", {"class": "text-container"})
                    .find("span", {"class": "extended-text__full"})
                    .get_text()
                    .replace("Скрыть", "")
                    .strip()
                )
            except AttributeError:
                return link.find("div", {"class": "text-container"}).get_text()

    def get_additional_info():
        """Возращает уточнения."""
        try:
            # Сначала выполняем поиск по элементу, в котором содержится
            # развернутое описание. Это позволяет избежать дублирования
            # текста.
            return (
                link.find("div", {"class": "text-container"})
                .find("span", {"class": "extended-text__full"})
                .get_text()
                .split("·", 1)[1]
                .replace("Скрыть", "")
                .strip()
            )
        except AttributeError:
            try:
                return (
                    link.find("div", {"class": "text-container"})
                    .get_text()
                    .split("·", 1)[1]
                    .strip()
                )
            except IndexError:
                return None
        except IndexError:
            return None

    def get_phone():
        try:
            return (
                link.find("span", {"class": "covered-phone__full"})
                .get_text()
                .strip()
            )
        except AttributeError:
            return None

    def get_work_hours():
        w_hours = None
        try:
            for div in link.find_all("div", {"class": "a11y-hidden"}):
                if "работы" in div.parent.get_text():
                    w_hours = (
                        div.parent.get_text()
                        .replace("Время работы", "")
                        .strip()
                    )
        except AttributeError:
            w_hours = None
        return w_hours

    def get_address():
        addr = None
        try:
            for div in link.find_all("div", {"class": "a11y-hidden"}):
                if "Адрес" in div.parent.get_text():
                    addr = div.parent.get_text().replace("Адрес", "").strip()
        except AttributeError:
            addr = None
        return addr

    def get_favicon():
        """Возвращает url фавикона."""
        return (
            "http://favicon.yandex.net/favicon/v2/"
            + website_link_text
            + "?size=32&stub=1"
        )

    def parse_site_links():
        """Преобразует быстрые ссылки, их текст и описания в один словарь"""
        sl_data = []
        if site_links_description is not None:
            for sl, slt, sld in zip(
                site_links, site_links_text, site_links_description
            ):
                sl_data.append(
                    {
                        "site_link": sl,
                        "site_link_text": slt,
                        "site_link_description": sld,
                    }
                )
        else:
            sld = None
            for (
                sl,
                slt,
            ) in zip(site_links, site_links_text):
                sl_data.append(
                    {
                        "site_link": sl,
                        "site_link_text": slt,
                        "site_link_description": sld,
                    }
                )
        return sl_data

    # Проверяем, не обрабатывается ли данный файл.
    file_path = "./small_files/filtered/" + file
    save_path = "./storage/fetched_data/" + file.replace(".txt", "")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(file_path) as text_file:
        for line in text_file:
            query = line.replace("\n", "").strip()
            print(query, flush=True)
            search_data = {"query": query, "results": []}

            links = get_search_results()
            if links is not None:
                for link in links:
                    try:
                        header = get_header()
                        second_header = get_second_header()
                        site_links = get_site_links()
                        site_links_text = get_site_links_text()
                        site_links_description = get_site_links_description()
                        if site_links is not None:
                            site_links_all = parse_site_links()
                        else:
                            site_links_all = None
                        website_link = get_website_link()
                        website_link_text = get_website_link_text()
                        product_link = get_product_link()
                        h2_link = get_link()
                        description = get_description()
                        additional_info = get_additional_info()
                        phone = get_phone()
                        work_hours = get_work_hours()
                        address = get_address()
                        favicon = get_favicon()

                        data = {
                            "header": header,
                            "second_header": second_header,
                            "site_links_all": site_links_all,
                            "site_links_text": site_links_text,
                            "website_link": website_link,
                            "website_link_text": website_link_text,
                            "product_link": product_link,
                            "h2_link": h2_link,
                            "description": description,
                            "additional_info": additional_info,
                            "phone": phone,
                            "work_hours": work_hours,
                            "address": address,
                            "favicon": favicon,
                        }

                        search_data["results"].append(data)

                    except AttributeError:
                        pass

                    try:
                        with open(
                            save_path + "/" + query + ".json", "w+"
                        ) as json_file:
                            results_json = json.dumps(search_data)
                            json_file.write(results_json)
                    except FileNotFoundError:
                        pass
    return None


if __name__ == "__main__":
    with Pool(processes=4) as pool:
        p1 = pool.apply_async(parser, args={files[0]})
        p2 = pool.apply_async(parser, args={files[1]})
        p3 = pool.apply_async(parser, args={files[2]})
        p4 = pool.apply_async(parser, args={files[3]})
        p5 = pool.apply_async(parser, args={files[4]})

        p1.get()
        p2.get()
        p3.get()
        p4.get()

    # Удаляем файлы, данные по которым уже были собраны.
    os.system("rm ./small_files/filtered/" + files[0])
    os.system("rm ./small_files/filtered/" + files[1])
    os.system("rm ./small_files/filtered/" + files[2])
    os.system("rm ./small_files/filtered/" + files[3])
    os.system("rm ./small_files/filtered/" + files[4])
