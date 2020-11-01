import requests
from bs4 import BeautifulSoup
import time

from Database.Db import DataBase
from libs.proxy import Proxy


class Sigma:
    def __init__(self):
        self.db = DataBase()
        self.proxy = Proxy()
        self.bookstore_id = 4

    def scraping_genre_url(self):
        list_of_genre_tuples = []

        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}

        source = s.get('https://www.knjizara-sigma.rs/map').text
        soup = BeautifulSoup(source, 'html.parser')

        genre_data = soup.find('div', class_='map-sections').find_all('li')
        for i in genre_data:
            genre_name = i.text.strip()
            genre_url = i.a['href']
            list_of_genre_tuples.append((genre_name, genre_url, self.bookstore_id))
        self.db.writing_genre_urls_in_db(list_of_genre_tuples)

    def get_genre_urls(self):
        rows = self.db.get_genre_urls_from_db(self.bookstore_id)
        for row in rows:
            self.scraping_book_urls(row[2], row[0])

    def scraping_book_urls(self, genre_url, genre_id):
        time.sleep(2)
        list_of_book_url_tuples = []
        num_of_pages = []

        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}

        source = s.get(genre_url).text
        soup = BeautifulSoup(source, 'html.parser')

        book_url_part = soup.find_all('div', class_='prod-item d-flex')
        for url in book_url_part:
            book_title = url.find('div', class_='prod-body d-flex flex-column').a.text
            book_url = url.find('div', class_='prod-body d-flex flex-column').a['href']
            list_of_book_url_tuples.append((book_title, book_url, genre_id, self.bookstore_id))
        print('db writing')
        self.db.writing_book_urls_in_db(list_of_book_url_tuples)

        if soup.find('ul', class_='pagination pagination-sm mb-0'):
            time.sleep(2)
            numbers = soup.find('ul', class_='pagination pagination-sm mb-0').find_all('li',
                                                                                       class_='page-item d-none d-lg-block')
            for i in numbers:
                num_of_pages.append(i.a.text)
            num_of_pages_int = num_of_pages[1:-1]
            for i in num_of_pages_int:
                print('next page')
                next_page_url = genre_url + '~pg' + i
                self.scraping_book_urls(next_page_url, genre_id)

    def get_book_urls(self):
        rows = self.db.get_book_urls_from_db(self.bookstore_id)
        for row in rows:
            self.scraping_book_info(row[2], row[3])

    def scraping_book_info(self, book_url, genre_id):
        time.sleep(2)
        description_all = []
        book_info_list_of_tuples = []

        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}

        source = s.get(book_url).text
        soup = BeautifulSoup(source, 'html.parser')

        if soup.find('div', class_='col-12 col-lg-auto col-gallery-buy mb-2'):
            book_cover = \
                soup.find('div', class_='col-12 col-lg-auto col-gallery-buy mb-2').find('img', id='prod_img_main')[
                    'src']
        else:
            book_cover = None

        title_and_author = soup.find('div', class_='col-12 col-lg col-prod-info').h1.text
        if title_and_author.find('-') != -1:
            title = title_and_author.split('-')[:-1][0]
        else:
            title = title_and_author

        description = None

        if soup.find('div', id="buy_prod_description"):
            desc = soup.find('div', id="buy_prod_description").find_all('p')
            for i in desc:
                description_all.append(i.text)
            description = ''
            for i in description_all:
                description += i

        if soup.find('div', class_='row-prod-specifications row-prod-price-old row-price'):
            price_without_discount = \
                soup.find('div', class_='row-prod-specifications row-prod-price-old row-price').text.strip().split(
                    'RSD')[0]
        else:
            price_without_discount = None

        if soup.find('div', class_='row-prod-specifications row-prod-price row-price'):
            online_price = \
                soup.find('div', class_='row-prod-specifications row-prod-price row-price').text.strip().split(' ')[0]
        else:
            online_price = None

        if soup.find('div', class_='row-prod-specifications row-prod-sku row-info'):
            isbn = soup.find('div', class_='row-prod-specifications row-prod-sku row-info').find('span',
                                                                                                 class_='prod-sku').text
        else:
            isbn = None

        if soup.find('div', class_='row-prod-specifications povez-knjige row-prop- row-info'):
            binding = soup.find('div', class_='row-prod-specifications povez-knjige row-prop- row-info').text.strip()
        else:
            binding = None

        if soup.find('div', class_='row-prod-specifications pismo row-prop- row-info'):
            letter = \
                soup.find('div', class_='row-prod-specifications pismo row-prop- row-info').text.strip().split(':')[1]
        else:
            letter = None

        if soup.find('div', class_='row-prod-specifications pisac row-prop- row-info'):
            author = \
                soup.find('div', class_='row-prod-specifications pisac row-prop- row-info').text.strip().split(':')[1]
        else:
            author = None

        if soup.find('div', class_='row-prod-specifications godina-izdanja-knjige row-prop- row-info'):
            year = soup.find('div',
                             class_='row-prod-specifications godina-izdanja-knjige row-prop- row-info').text.strip().split(
                ':')[1]
        else:
            year = None

        if soup.find('div', class_='row-prod-specifications izdavač row-prop- row-info'):
            publisher = \
                soup.find('div', class_='row-prod-specifications izdavač row-prop- row-info').text.strip().split(':')[1]
        else:
            publisher = None

        id_number = None
        number_of_pages = None
        book_format = None
        rating = None
        comments = None

        book_info_list_of_tuples.append(
            (title, author, book_cover, description, price_without_discount, online_price, publisher, id_number, isbn,
             year, letter, binding, book_format, number_of_pages, genre_id, rating, comments, self.bookstore_id))
        self.db.writing_book_info_in_db(book_info_list_of_tuples)
