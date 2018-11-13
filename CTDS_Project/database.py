import sqlite3 as sql

class Database:

    def __init__(self):
        self.con = sql.connect('wikipedia.sqlite')
        self.c = self.con.cursor()
        self.create_table()

    def create_table(self):
        try:
            self.c.execute('CREATE TABLE articles(name TEXT PRIMARY KEY, signature BLOB)')
            self.con.commit()
        except sql.OperationalError:
            pass

    def add_article(self, article, signature):
        self.c.execute('INSERT INTO articles VALUES("{}","{}")'.format(article, str(signature)))
        self.con.commit()

    def get_signature(self, article):
        self.c.execute('SELECT signature FROM articles WHERE name = "{}"'.format(article))
        return list(map(int, self.c.fetchone()[0][1:-1].split(', ')))

    def close(self):
        self.con.close()

db = Database()
# db.add_article('Test', [1,2,3,4,5])
signature = db.get_signature('Test')
print(signature)
db.close()