import sqlite3 as sql

class Database:

    def __init__(self):
        self.con = sql.connect('wikipedia.sqlite')
        self.c = self.con.cursor()
        self.create_table()

    def create_table(self):
        try:
            self.c.execute('CREATE TABLE articles(name TEXT PRIMARY KEY, signature BLOB)')
        except sql.OperationalError:
            pass

    def add_article(self, article, signature):
        pass

    def get_article(self, article):
        pass

    def close(self):
        self.con.close()

db = Database()
db.close()