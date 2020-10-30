import requests
from bs4 import BeautifulSoup
import time

from Database.Db import DataBase
from libs.proxy import Proxy


class Dereta:
    def __init__(self):
        self.db = DataBase()
        self.proxy = Proxy()
        self.bookstore_id = 3

    def scraping_genre_url(self):
        list_of_genre_tuples = []

        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}

        source = s.get('https://dereta.rs/knjizara.aspx').text
        soup = BeautifulSoup(source, 'html.parser')

        genre_data = soup.find('div', id='group-panel').find_all('a', class_='group-item')
        for i in genre_data:
            genre_url = 'https://dereta.rs/' + i['href']
            genre_name = i.text
            data = (genre_name, genre_url, self.bookstore_id)
            list_of_genre_tuples.append(data)
        self.db.writing_genre_urls_in_db(list_of_genre_tuples)

    def get_genre_urls(self):
        rows = self.db.get_genre_urls_from_db(self.bookstore_id)
        for i in rows:
            self.scraping_book_urls(i[2], i[0])

    def scraping_book_urls(self, genre_url, genre_id):
        time.sleep(2)
        list_of_book_url_tuples = []

        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}

        source = s.get(genre_url).text
        soup = BeautifulSoup(source, 'html.parser')

        book_urls = soup.find_all('div', class_='col-xs-6 col-sm-4 col-lg-3 col-md-3')
        for url in book_urls:
            book_url_part = url.find('a', class_='product-title')['href']
            book_url = 'https://dereta.rs/' + book_url_part
            book_title = url.find('a', class_='product-title').text.strip()
            list_of_book_url_tuples.append((book_title, book_url, genre_id, self.bookstore_id))
        self.db.writing_book_urls_in_db(list_of_book_url_tuples)

        try:
            next_page = soup.find('div', class_='mypager')
            next_page1 = next_page.find('a', title='Next')['href']
            next_page_url = 'https://dereta.rs/' + next_page1
            # act_num_of_page = next_page.find('a', class_='pager-selected')
            # print(act_num_of_page)
            if next_page:
                print(next_page_url)
                self.scraping_book_urls(next_page_url, genre_id)
                time.sleep(2)
        except:
            print('This category is scraped')

    def get_book_urls(self):
        rows = self.db.get_book_urls_from_db(self.bookstore_id)
        for i in rows:
            time.sleep(0.5)
            self.scraping_book_info(i[2], i[3])

    def scraping_book_info(self, book_url, genre_id):
        time.sleep(2)
        specification_elements = []
        book_info_list_of_tuples = []

        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}

        source = s.get(book_url).text
        soup = BeautifulSoup(source, 'html.parser')

        book_cover = None
        rating = None
        comments = None

        element = soup.find_all('div', class_='col-sm-12 col-lg-12 col-md-12')
        title = element[1].h1.a.text
        author = element[1].h2.text.strip()
        if element[2].text:
            description = element[2].text.split(':')[1].strip()
        else:
            description = None

        specification = soup.find('div', id='PrintedBookAtributtes').find_all('span')
        for i in specification:
            specification_elements.append(i.text)
        spec_el_dct = {specification_elements[i]: specification_elements[i + 1] for i in
                       range(0, len(specification_elements), 2)}

        if soup.find('div', class_='book_basket').find('div', class_='text_wrap'):
            price_without_discount = soup.find('div', class_='book_basket').find('div', class_='text_wrap').text.strip()
            price_without_discount = price_without_discount.split(':')[1].strip().split(' ')[0]
        else:
            price_without_discount = None

        if soup.find('div',
                     id="ctl00_ctl00_CMSWebPartManager_MainProductPreview_MainProductPreviewTitle_ctl00_rptItem_Panel998_0").select_one(
            'div.text_wrap > b'):
            online_price = soup.find('div',
                                     id="ctl00_ctl00_CMSWebPartManager_MainProductPreview_MainProductPreviewTitle_ctl00_rptItem_Panel998_0").select_one(
                'div.text_wrap > b').text.strip().split(' ')[0]
        else:
            online_price = None

        id_number = None
        publisher = None
        year = None
        isbn = None
        number_of_pages = None
        letter = None
        binding = None
        book_format = None

        for key, value in spec_el_dct.items():
            if 'IzdavaÄ\x8d:' in key:
                publisher = value
            if 'Godina izdanja:' in key:
                year = value
            if 'ISBN:' in key:
                isbn = value
            if 'Br. str.:' in key:
                number_of_pages = value
            if 'Pismo:' in key:
                letter = value
            if 'Povez:' in key:
                binding = value
            if 'Format:' in key:
                book_format = value

        book_info_list_of_tuples.append(
            (title, author, book_cover, description, price_without_discount, online_price, publisher, id_number, isbn,
             year, letter, binding, book_format, number_of_pages, genre_id, rating, comments, self.bookstore_id))
        self.db.writing_book_info_in_db(book_info_list_of_tuples)
