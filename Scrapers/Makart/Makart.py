import requests
from bs4 import BeautifulSoup
import time

from Database.Db import DataBase
from libs.proxy import Proxy


class Makart:
    def __init__(self):
        self.db = DataBase()
        self.proxy = Proxy()
        self.bookstore_id = 5

    def scraping_genre_urls(self):
        list_of_genre_tuples = []

        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}

        source = requests.get('https://www.makart.rs/knjige').text
        soup = BeautifulSoup(source, 'html.parser')

        genres = soup.find('ul', id='sidebar-zanrovi').find_all('li')
        for i in genres:
            genre_name = i.a.text
            genre_url = 'https://www.makart.rs/' + i.a['href']
            list_of_genre_tuples.append((genre_name, genre_url, self.bookstore_id))
        self.db.writing_genre_urls_in_db(list_of_genre_tuples)

    def get_genre_urls(self):
        rows = self.db.get_genre_urls_from_db(self.bookstore_id)
        for row in rows:
            self.scraping_book_urls(row[2], row[0])

    def scraping_book_urls(self, genre_url, genre_id):
        list_of_book_url_tuples = []
        time.sleep(2)

        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}

        source = requests.get(genre_url).text
        soup = BeautifulSoup(source, 'html.parser')

        books = soup.find_all('div', class_='col-xs-6 col-sm-6 col-md-4 col-lg-3')
        for i in books:
            book_url = 'https://www.makart.rs/' + i.a['href']
            book_title = i.find('div', class_='tg-booktitle').text
            list_of_book_url_tuples.append((book_title, book_url, genre_id, self.bookstore_id))
        self.db.writing_book_urls_in_db(list_of_book_url_tuples)

        if soup.find('ul', class_='pagination'):
            next_page = soup.find('ul', class_='pagination').find_all('a')[-1]['href']
            url = 'https://www.makart.rs/' + next_page
            self.scraping_book_urls(url, genre_id)

    def get_book_urls(self):
        rows = self.db.get_book_urls_from_db(self.bookstore_id)
        for row in rows:
            self.scraping_book_info(row[2], row[3])

    def scraping_book_info(self, book_url, genre_id):
        book_info_list_of_tuples = []

        time.sleep(1)
        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}

        source = requests.get(book_url).text
        soup = BeautifulSoup(source, 'html.parser')

        if soup.find('div', class_='col-xs-12 col-sm-5 col-md-4 col-lg-4'):
            cover = \
            soup.find('div', class_='col-xs-12 col-sm-5 col-md-4 col-lg-4').select_one('figure.tg-featureimg > img')[
                'src']
            book_cover = 'https://www.makart.rs/' + cover
        else:
            book_cover = None

        data = soup.find('div', class_='col-xs-12 col-sm-7 col-md-8 col-lg-8')
        if data.find('div', class_='tg-booktitle'):
            title = data.find('div', class_='tg-booktitle').text.strip()
        else:
            title = None

        if data.find('span', class_='tg-bookwriter'):
            author = data.find('span', class_='tg-bookwriter').text.strip()
        else:
            author = None

        if data.find('div', class_='izdavac'):
            publisher = data.find('div', class_='izdavac').text
        else:
            publisher = None

        if data.find('div', class_='col-md-12 col-lg-6').find('span', class_='tg-bookprice'):
            price = data.find('div', class_='col-md-12 col-lg-6').find('span', class_='tg-bookprice')
            price_without_discount = price.text.strip().split('rsd')[1].strip() + ',00'
            online_price = price.text.strip().split('rsd')[0].strip() + ',00'
        else:
            price_without_discount = None
            online_price = None

        if soup.find('div', class_='tg-tab-content tab-content').find('div', class_='tg-description'):
            description = soup.find('div', class_='tg-tab-content tab-content').find('div', class_='tg-description').text
        else:
            description = None

        comments = None
        rating = None
        id_number = None
        isbn = None
        number_of_pages = None
        letter = None
        binding = None
        book_format = None
        year = None

        specification = soup.find('div', class_='tg-widgetcontent1').ul.find_all('li')
        for i in specification:
            if i.text.split(':')[0] == 'ISBN':
                isbn = i.text.split(':')[1]
            if i.text.split(':')[0] == 'Broj strana':
                number_of_pages = i.text.split(':')[1]
            if i.text.split(':')[0] == 'Pismo':
                letter = i.text.split(':')[1]
            if i.text.split(':')[0] == 'Povez':
                binding = i.text.split(':')[1]
            if i.text.split(':')[0] == 'Format':
                book_format = i.text.split(':')[1]
            if i.text.split(':')[0] == 'Godina izdanja':
                year = i.text.split(':')[1]

        book_info_list_of_tuples.append(
            (title, author, book_cover, description, price_without_discount, online_price, publisher, id_number, isbn,
             year, letter, binding, book_format, number_of_pages, genre_id, rating, comments, self.bookstore_id))
        self.db.writing_book_info_in_db(book_info_list_of_tuples)

