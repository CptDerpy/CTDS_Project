import sqlite3 as sql

class Database:

    def __init__(self):
        self.con = sql.connect('wikipedia.sqlite')
        # SELECT returns list of single values instead of tuples:
        self.con.row_factory = lambda cursor, row: row[0]
        self.c = self.con.cursor()
        self.create_table()

    def create_table(self):
        try:
            self.c.execute('CREATE TABLE articles(name TEXT, value INTEGER)')
            self.con.commit()
        except sql.OperationalError:
            pass

    def add_article(self, article, signature):
        for value in signature:
            self.c.execute('INSERT INTO articles VALUES("{}",{})'.format(article, value))
        self.con.commit()

    def get_signature(self, article):
        self.c.execute('SELECT value FROM articles WHERE name = "{}"'.format(article))
        return self.c.fetchall()

    def close(self):
        self.con.close()

db = Database()
db.add_article('Test', [1,2,3,4,5])
signature = db.get_signature('Test')
print(signature)
db.close()