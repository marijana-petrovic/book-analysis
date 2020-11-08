import requests
from bs4 import BeautifulSoup
import time

from Database.Db import DataBase
from libs.proxy import proxy_settings
from Scrapers.Dereta.Dereta import Dereta
from Scrapers.Dereta.HtmlParser import HtmlParser


class Info(Dereta):
    def __init__(self):
        Dereta.__init__(self)
        self.db = DataBase()
        self.html_parser = HtmlParser()
        self.__start()

    def __start(self):
        rows = self.db.get_book_urls_from_db(self.bookstore_id)
        for i in rows:
            time.sleep(0.5)
            self.__scrape(i[2], i[3])

    def __scrape(self, book_url, category_id):
        time.sleep(2)
        s = requests.Session()
        s.proxies = {proxy_settings}

        source = s.get(book_url).text
        soup = BeautifulSoup(source, 'html.parser')

        book_info = self.html_parser.parse_book_info_html(soup, category_id)
        self.db.writing_book_info_in_db(book_info)
