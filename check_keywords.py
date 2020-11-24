import os
import json
import idna
import string
import random
from multiprocessing import Pool
from idna import IDNAError
from idna.core import InvalidCodepoint

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ChunkedEncodingError, ConnectionError

from app import db
from app.models import KeywordsDomain


city_id = "213"
files = os.listdir("./small_files/filtered")
#with open("./query_list.txt", "r") as text_file:
#    text_data = text_file.readlines()

# request_data = []
# for i in text_data:
#    request_data.append(i.replace("\n", ""))


def parser(file):
    def get_search_results():
        """Возвращает список ссылок, собранных из выдачи поиска по
        Яндекс-директ, в виде html-кода."""
        try:
            
            #if query in request_data:
            #    return None
            
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
        except ConnectionError:
            return None

    def get_header():
        try:
            head = link.find("h2").get_text()
        except AttributeError:
            head = "null"

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
            return "null"
        except AttributeError:
            return "null"

    def get_site_links():
        """Быстрые ссылки. ОТОБРАЖАТЬ НЕ БУДЕМ."""
        s_links = []
        try:
            for a in link.find("div", {"class": "sitelinks"}).find_all("a"):
                s_links.append(a.attrs["href"])
        except AttributeError:
            s_links = "null"
        if len(s_links) == 0:
            s_links = "null"
        return s_links

    def get_site_links_text():
        sl_descriptions = []
        try:
            for a in link.find("div", {"class": "sitelinks"}).find_all("a"):
                sl_descriptions.append(a.get_text())
        except AttributeError:
            sl_descriptions = "null"
        if len(sl_descriptions) == 0:
            sl_descriptions = "null"
        return sl_descriptions

    def get_site_links_description():
        sl_desc = []
        try:
            for div in link.find_all("div", {"class": "sitelinks__desc"}):
                sl_desc.append(div.get_text())
        except AttributeError:
            pass

        if len(sl_desc) == 0:
            sl_desc = "null"

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
            return "null"

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
                return "null"
        except IndexError:
            return "null"

    def get_phone():
        try:
            return (
                link.find("span", {"class": "covered-phone__full"})
                .get_text()
                .strip()
            )
        except AttributeError:
            return "null"

    def get_work_hours():
        w_hours = "null"
        try:
            for div in link.find_all("div", {"class": "a11y-hidden"}):
                if "работы" in div.parent.get_text():
                    w_hours = (
                        div.parent.get_text()
                        .replace("Время работы", "")
                        .strip()
                    )
        except AttributeError:
            w_hours = "null"
        return w_hours

    def get_address():
        addr = "null"
        try:
            for div in link.find_all("div", {"class": "a11y-hidden"}):
                if "Адрес" in div.parent.get_text():
                    addr = div.parent.get_text().replace("Адрес", "").strip()
        except AttributeError:
            addr = "null"
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
        if site_links_description != "null":
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
            sld = "null"
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
    save_path = "domain_data"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(file_path) as text_file:
        for line in text_file:
            query = line.replace("\n", "").strip()
            print(query, flush=True)

            links = get_search_results()
            if links is not None:
                for link in links:
                    try:
                        header = get_header()
                        second_header = get_second_header()
                        site_links = get_site_links()
                        site_links_text = get_site_links_text()
                        site_links_description = get_site_links_description()
                        if site_links != "null":
                            site_links_all = parse_site_links()
                        else:
                            site_links_all = "null"
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
                        search_data = {"query": query, "ad": data}
                        # Записываем собранные данные в директорию, принадлежащую домену,
                        # либо создаем для домена новую директорию.
                        domain_dir_name = website_link_text.replace(".", "_")
                        save_path = f"domain_data/{domain_dir_name}/"
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

                        result_data = json.dumps(search_data)
                        with open(save_path + file_name + ".json", "w") as json_file:
                            json_file.write(result_data)                            
                        
                    except AttributeError:
                        pass

    return None


if __name__ == "__main__":
    with Pool(processes=1) as pool:
        p1 = pool.apply_async(parser, args={files[0]})
        #p2 = pool.apply_async(parser, args={files[1]})
        #p3 = pool.apply_async(parser, args={files[2]})
        #p4 = pool.apply_async(parser, args={files[3]})
        #p5 = pool.apply_async(parser, args={files[4]})        
        #p6 = pool.apply_async(parser, args={files[5]})
        #p7 = pool.apply_async(parser, args={files[6]})
        #p8 = pool.apply_async(parser, args={files[7]})
        #p9 = pool.apply_async(parser, args={files[8]})
        #p10 = pool.apply_async(parser, args={files[9]})

        p1.get()
        #p2.get()
        #p3.get()
        #p4.get()
        #p5.get()
        #p6.get()
        #p7.get()
        #p8.get()
        #p9.get()
        #p10.get()

    # Удаляем файлы, данные по которым уже были собраны.
    os.system("rm ./small_files/filtered/" + files[0])
    #os.system("rm ./small_files/filtered/" + files[1])
    #os.system("rm ./small_files/filtered/" + files[2])
    #os.system("rm ./small_files/filtered/" + files[3])
    #os.system("rm ./small_files/filtered/" + files[4])
    #os.system("rm ./small_files/filtered/" + files[5])
    #os.system("rm ./small_files/filtered/" + files[6])
    #os.system("rm ./small_files/filtered/" + files[7])
    #os.system("rm ./small_files/filtered/" + files[8])
    #os.system("rm ./small_files/filtered/" + files[9])
