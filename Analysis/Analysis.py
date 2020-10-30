# instalirani mysqlclient i SQLAlchemy
import pandas as pd
import numpy as np
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

    def plot_top_15_authors(self):
        fig, ax = plt.subplots()
        plt.barh(self.top_15_authors, self.num_of_books_top_15, color='maroon')

        plt.xlabel("Number of published books")
        plt.ylabel("Author")
        plt.title("Published books by the authors")
        ax.invert_yaxis()  # labels read top-to-bottom
        plt.show()
        # plt.savefig('top15Authors.png')

    def authors_performance(self):
        # test out the performance of these authors
        book_name = []
        book_rating = []

        a_performance = database.get_authors_performance(self.top_15_authors[5])

        for book in a_performance:
            book_name.append(book[1])
            book_rating.append(book[2])

        plt.barh(book_name, book_rating, align='center', color='maroon')

        plt.xlabel("Book rating")
        plt.ylabel("Book name")
        plt.title("Performance of " + self.top_15_authors[5])
        plt.show()
        # plt.savefig('authorsPerformance.png')

    def top_rated_books(self):
        top_rated_authors = []
        rating_count = []

        plt.rcParams.update({'font.size': 10})

        top_rat_authors = database.get_top_rated_authors()
        for author in top_rat_authors:
            top_rated_authors.append(author[0])
            rating_count.append(author[1])

        plt.figure(figsize=(15, 20))
        plt.subplot(111)
        plt.barh(top_rated_authors, rating_count, align='center', height=0.5, color='maroon')
        plt.xlabel("Number of 5 star ratings")
        plt.ylabel("Author")
        plt.title("Top rated authors")
        plt.xticks(np.arange(6), (0,1,2,3,4,5))
        plt.gca().invert_yaxis()
        plt.tight_layout()

        plt.show()
        # plt.savefig('topRatedBooks.png')
        

plot = Plot()
plot.top_rated_books()
