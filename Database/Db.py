import mysql.connector


class DataBase:
    def __init__(self):
        self.cnx = mysql.connector.connect(user='', password='', host='', database='')
        self.cursor = self.cnx.cursor()

    def execute_many(self, query, values):
        self.cursor.executemany(query, values)
        self.cnx.commit()

    def execute_(self, query, values=()):
        self.cursor.execute(query, values)
        rows = self.cursor.fetchall()
        return rows

    def writing_genre_urls_in_db(self, genre_tuples):
        self.execute_many("INSERT INTO genre_urls"
                          "(genre_name, genre_url, bookstore)"
                          "VALUES (%s, %s, %s)", genre_tuples)

    def get_genre_urls_from_db(self, bookstore_id):
        return self.execute_("SELECT * FROM genre_urls WHERE bookstore=%s", (bookstore_id,))

    def writing_book_urls_in_db(self, book_tuples):
        self.execute_many("INSERT INTO book_urls"
                          "(book_title, book_url, genre_id, bookstore_id)"
                          "VALUES (%s, %s, %s, %s)", book_tuples)

    def get_book_urls_from_db(self, bookstore_id):
        return self.execute_("SELECT * FROM book_urls WHERE bookstore_id=%s", (bookstore_id,))

    def writing_book_info_in_db(self, book_info_tuples):
        self.execute_many("INSERT INTO book_info"
                          "(title, author, book_cover, description, price_without_discount, online_price, publisher,"
                          "id_number, isbn, year, letter, binding, book_format, number_of_pages, category_id, rating, comments, bookstore_id)"
                          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                          book_info_tuples)

    def get_book_data_from_db(self):
        return self.execute_("SELECT * FROM book_info")

    def get_top_15(self):
        return self.execute_(
            "SELECT author,  COUNT(book_id) as count FROM books.book_info GROUP BY author ORDER BY count DESC LIMIT 15")

    def get_authors_performance(self, author):
        return self.execute_("SELECT author, title, rating FROM books.book_info WHERE author =%s ORDER BY rating", (author,))

    def get_top_rated_authors(self):
        return self.execute_("SELECT DISTINCT author, COUNT(book_id) AS count FROM books.book_info WHERE rating = 5 GROUP BY author ORDER BY COUNT(book_id) DESC")