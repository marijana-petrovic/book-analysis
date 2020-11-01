import requests
from bs4 import BeautifulSoup
import time

from Database.Db import DataBase
from libs.proxy import Proxy


class Vulkan:
    def __init__(self):
        self.db = DataBase()
        self.proxy = Proxy()
        self.bookstore_id = 2

    def scraping_genre_urls(self):
        links = []
        names = []
        bookstore = []

        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}
        source = s.get('https://www.knjizare-vulkan.rs/').text
        soup = BeautifulSoup(source, 'html.parser')

        cat_links = soup.select('ul.nav-main-submenu > li > a')

        for link in cat_links:
            names.append(link.text)
            links.append(link['href'])
            bookstore.append(self.bookstore_id)

        zipped = zip(names, links, bookstore)
        self.db.writing_genre_urls_in_db(zipped)

    def get_genre_urls(self):
        rows = self.db.get_genre_urls_from_db(self.bookstore_id)
        for row in rows:
            time.sleep(0.5)
            self.scraping_book_urls(row[2], row[0])

    def scraping_book_urls(self, genre_urls, genre_id):
        book_titles = []
        book_links = []
        genre_idnum = []
        bookstore_idnum = []

        time.sleep(1)
        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}
        source = s.get(genre_urls).text
        soup = BeautifulSoup(source, 'html.parser')

        article = soup.find_all('div',
                                class_='wrapper-gridalt-view item product-item ease col-xs-6 col-sm-3 col-md-2 col-lg-2 gridalt-view')
        for i in article:
            book_links.append(i.find('div', class_='title').a['href'])
            book_titles.append(i.find('div', class_='title').text.strip())
            genre_idnum.append(genre_id)
            bookstore_idnum.append(self.bookstore_id)

        book_data = zip(book_titles, book_links, genre_idnum, bookstore_idnum)
        self.db.writing_book_urls_in_db(book_data)

        pagination = soup.find('ul', class_='pagination')
        next_page = pagination.find('li', class_='next first-last')
        act_num_of_page = pagination.find('li', class_='number active').a.text

        if next_page:
            if genre_urls.find('/page-') > 0:
                book_link = genre_urls.split('/')[:-1]
                book_link = '/'.join([str(elem) for elem in book_link]) + '/page-' + act_num_of_page
            else:
                book_link = genre_urls + '/page-' + act_num_of_page

            print('Skrejpovana next strana: ' + book_link)
            self.scraping_book_urls(book_link, genre_id)

    def get_book_urls(self):
        rows = self.db.get_book_urls_from_db(self.bookstore_id)
        for row in rows:
            time.sleep(0.3)
            self.scraping_book_info(row[2], row[3])

    def scraping_book_info(self, book_url, category_id):
        book_info_list = []

        time.sleep(0.3)
        s = requests.Session()
        s.proxies = {self.proxy.proxy_settings}
        source = s.get(book_url).text
        soup = BeautifulSoup(source, 'html.parser')

        if soup.find('div', class_='col-xs-12 col-sm-6 product-detail-wrapper').find('div', class_='title'):
            title = soup.find('div', class_='col-xs-12 col-sm-6 product-detail-wrapper').find('div',
                                                                                              class_='title').text.strip()
        else:
            title = None

        if soup.find('div', class_='code'):
            isbn = soup.find('div', class_='code').text.strip().split(':')[2]
        else:
            isbn = None

        if soup.find('div', class_='code'):
            id_number = soup.find('div', class_='code').text.strip().split(':')[1].split("\n")[0]
        else:
            id_number = None

        desc = soup.find('div', class_='tab-content').find('div', id='tab_product_description')
        if desc:
            description = soup.find('div', class_='tab-content').find('div', id='tab_product_description').text.strip()
        else:
            description = None

        if soup.find('div', class_='block product-images'):
            book_cover = soup.find('div', class_='block product-images').img['data-real-linkg']
        else:
            book_cover = None

        price_on_the_site = soup.find('div', class_='block product-details-price')
        if price_on_the_site:
            online_price = price_on_the_site.find('span', class_='product-price-value value').text
        else:
            online_price = None

        full_price = soup.find('div', class_='prev-price product-prev-price product-pricewithoutdiscount')
        if full_price:
            price_without_discount = full_price.find('span', class_='product-price-without-discount-value value').text
        else:
            price_without_discount = 'Not available'

        author = None
        publisher = None
        letter = None
        binding = None
        year = None
        book_format = None
        number_of_pages = None
        rating = None
        comments = None

        spec = soup.find('div', class_="block product-tab-specification").tbody
        specification = spec.find_all('tr')
        for i in specification:
            element = i.find_all('td')
            left = element[0].text.strip()
            right = element[1].text.strip()
            if left == "Autor":
                author = right
            if left == "Izdavač":
                publisher = right
            if left == "Pismo":
                letter = right
            if left == "Povez":
                binding = right
            if left == "Godina":
                year = right
            if left == "Format":
                book_format = right
            if left == "Strana":
                number_of_pages = right

        book_info_list.append((title, author, book_cover, description, price_without_discount, online_price, publisher,
                               id_number, isbn, year, letter, binding, book_format, number_of_pages, category_id,
                               rating, comments, self.bookstore_id))
        self.db.writing_book_info_in_db(book_info_list)
