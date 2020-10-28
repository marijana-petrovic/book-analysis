# instalirani mysqlclient i SQLAlchemy
import pandas as pd
import matplotlib.pyplot as plt
from Database.Db import DataBase

database = DataBase()

# assign a variable that contains a string of your credentials
credentials = "mysql://"


class Plot:
    def __init__(self):
        self.top_15_authors = []
        self.num_of_books_top_15 = []

        rows = database.get_top_15()
        for row in rows:
            self.top_15_authors.append(row[0])
            self.num_of_books_top_15.append(row[1])

    def plot_top_15(self):
        fig, ax = plt.subplots()
        plt.barh(self.top_15_authors, self.num_of_books_top_15, color='maroon')

        plt.xlabel("Number of published books")
        plt.ylabel("Author")
        plt.title("Published books by the authors")
        ax.invert_yaxis()  # labels read top-to-bottom
        plt.show()

    def authors_performance(self):
        # test out the performance of these authors
        book_name = []
        book_rating = []

        a_performance = database.authors_performance(self.top_15_authors[5])

        for book in a_performance:
            book_name.append(book[1])
            book_rating.append(book[2])

        plt.barh(book_name, book_rating, align='center', color='maroon')

        plt.xlabel("Book rating")
        plt.ylabel("Book name")
        plt.title('Performance of ' + self.top_15_authors[5])
        plt.show()
        # plt.savefig('authorsPerformance.png')

    def top_15_most_rated_books(self):
        pass


plot = Plot()
# plot.plot_top_15()
plot.authors_performance()
