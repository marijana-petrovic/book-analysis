import requests
from bs4 import BeautifulSoup
import time

from Database.Db import DataBase
from libs.proxy import proxy_settings
from Scrapers.Delfi.Delfi import Delfi
from Scrapers.Delfi.HtmlParser import HtmlParser


class Info(Delfi):

    def __init__(self):
        Delfi.__init__(self)
        self.db = DataBase()
        self.html_parser = HtmlParser()
        self.__start()

    def __start(self):
        rows = self.db.get_book_urls_from_db(self.bookstore_id)
        for row in rows:
            time.sleep(0.2)
            self.__scrape(row[2], row[3])

    def __scrape(self, url, category_id):
        time.sleep(1)
        s = requests.Session()
        s.proxies = {proxy_settings}

        source = s.get(url).text
        soup = BeautifulSoup(source, 'html.parser')

        book_info = self.html_parser.parse_book_info_html(soup, category_id)
        self.db.writing_book_info_in_db(book_info)