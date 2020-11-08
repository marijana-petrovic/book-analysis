import requests
from bs4 import BeautifulSoup
import time

from Database.Db import DataBase
from libs.proxy import proxy_settings
from Scrapers.Delfi.Delfi import Delfi
from Scrapers.Delfi.HtmlParser import HtmlParser


class Links(Delfi):
    def __init__(self):
        Delfi.__init__(self)
        self.db = DataBase()
        self.html_parser = HtmlParser()
        self.__start()

    def __start(self):
        rows = self.db.get_genre_urls_from_db(self.bookstore_id)
        for i in rows:
            time.sleep(0.5)
            self.__scrape(i[2], i[0])

    def __scrape(self, url, genre_id):
        time.sleep(0.3)
        s = requests.Session()
        s.proxies = {proxy_settings}

        source = s.get(url).text
        soup = BeautifulSoup(source, 'html.parser')

        list_of_books_tuple = self.html_parser.parse_book_url_html(soup, genre_id)
        self.db.writing_book_urls_in_db(list_of_books_tuple)

        pagination = self.html_parser.check_pagination(soup)
        if pagination:
            self.__scrape(pagination, genre_id)
