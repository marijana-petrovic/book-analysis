import requests
from bs4 import BeautifulSoup
import time

from Database.Db import DataBase
from libs.proxy import proxy_settings
from Scrapers.Dereta.Dereta import Dereta
from Scrapers.Dereta.HtmlParser import HtmlParser


class Links(Dereta):
    def __init__(self):
        Dereta.__init__(self)
        self.db = DataBase()
        self.html_parser = HtmlParser()
        self.__start()

    def __start(self):
        rows = self.db.get_genre_urls_from_db(self.bookstore_id)
        for i in rows:
            self.__scrape(i[2], i[0])

    def __scrape(self, genre_url, genre_id):
        time.sleep(2)
        s = requests.Session()
        s.proxies = {proxy_settings}

        source = s.get(genre_url).text
        soup = BeautifulSoup(source, 'html.parser')

        list_of_book_url_tuples = self.html_parser.parse_book_url_html(soup, genre_id)
        self.db.writing_book_urls_in_db(list_of_book_url_tuples)
