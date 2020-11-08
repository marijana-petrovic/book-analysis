from Scrapers.Delfi.Delfi import Delfi


class HtmlParser(Delfi):
    def __init__(self):
        Delfi.__init__(self)

    def parse_category_url(self, soup):
        list_of_genre_tuples = []
        genre = soup.find('ul', id='zanrovi').find_all('li')
        for i in genre:
            genre_name = i.a.text
            genre_url = i.a['href']
            list_of_genre_tuples.append((genre_name, genre_url, self.bookstore_id))
        return list_of_genre_tuples

    def parse_book_url_html(self, soup, genre_id):
        list_of_books_tuple = []
        book_urls = soup.find_all('div', class_='carousel-book-info')

        for url in book_urls:
            book_title = url.h3.a.text
            book_url = url.h3.a['href']
            genre_idnum = genre_id
            bookstore_id = self.bookstore_id

            list_of_books_tuple.append((book_title, book_url, genre_idnum, bookstore_id))
        return list_of_books_tuple

    def check_pagination(self, soup):
        pagination = soup.find('a', rel='next')
        if pagination:
            link = pagination['href']
            return link
        else:
            return False

    def parse_book_info_html(self, soup, category_id):
        book_info_list_of_tuples = []
        list_left = []
        list_right = []

        book_cover = None
        title = None
        author = None
        publisher = None
        rating = None
        price_without_discount = None
        online_price = None
        description = None
        comments = None

        col = soup.find('div', class_='col product-holder')
        if col.find('div', class_='media-image').img['src']:
            book_cover = col.find('div', class_='media-image').img['src']
        if col.find('div', class_='media-body').h1.text:
            title = col.find('div', class_='media-body').h1.text
        if col.select_one('div.media-body > p'):
            author = col.select_one('div.media-body > p').text.strip()
        if col.select('div.media-body > p'):
            publisher = col.select('div.media-body > p')[1].text.split(':')[1]
        if col.find('span', class_='rating-stars').span:
            rating = col.find('span', class_='rating-stars').span.text

        if col.select('div.product-price > p'):
            if col.find('p', class_='cena-u-knjizarama'):
                price_without_discount = col.find('p', class_='cena-u-knjizarama').text.split(':')[1][:-3]
            if col.find('p', class_='cena-na-sajtu').span:
                online_price = col.find('p', class_='cena-na-sajtu').span.text.split(' ')[0]
            else:
                online_price = col.find('p', class_='cena-na-sajtu').text.split(':')[1]

        tabs = soup.find('div', class_='col product-tabs').find('div', class_='tab-content style-2')
        if tabs.find('div', style='text-align: justify;'):
            description = tabs.find('div', style='text-align: justify;').text
        if tabs.find('div', class_='tab-pane komentari').find('div', class_='col-12'):
            comments = tabs.find('div', class_='tab-pane komentari').find('div', class_='col-12').text.strip()
        specification = tabs.find('div', class_='tab-pane podaci')

        left = specification.find('div', class_='col-left').find_all('p')
        right = specification.find('div', class_='col-right').find_all('p')
        for el in left:
            list_left.append(el.text)
        for el2 in right:
            list_right.append(el2.text)
        zipped = zip(list_left, list_right)

        id_number = None
        isbn = None
        number_of_pages = None
        letter = None
        binding = None
        book_format = None
        year = None

        for el in zipped:
            if el[0] == 'nav-id:':
                id_number = el[1]
            if el[0] == 'ISBN:':
                isbn = el[1]
            if el[0] == 'Broj strana:':
                number_of_pages = el[1]
            if el[0] == 'Pismo:':
                letter = el[1]
            if el[0] == 'Povez:':
                binding = el[1]
            if el[0] == 'Format:':
                book_format = el[1]

        book_info_list_of_tuples.append(
            (title, author, book_cover, description, price_without_discount, online_price, publisher, id_number, isbn,
             year, letter, binding, book_format, number_of_pages, category_id, rating, comments, self.bookstore_id))
        return book_info_list_of_tuples


