import requests
from bs4 import BeautifulSoup

from Database.Db import DataBase
from libs.proxy import proxy_settings
from Scrapers.Delfi.Delfi import Delfi
from Scrapers.Delfi.HtmlParser import HtmlParser


class Category(Delfi):

    def __init__(self):
        Delfi.__init__(self)
        self.db = DataBase()
        self.html_parser = HtmlParser()
        self.__start()

    def __start(self):
        s = requests.Session()
        s.proxies = {proxy_settings}

        source = s.get(self.bookstore_category_link).text
        soup = BeautifulSoup(source, 'html.parser')

        list_of_genre_tuples = self.html_parser.parse_category_url(soup)
        self.db.writing_genre_urls_in_db(list_of_genre_tuples)
