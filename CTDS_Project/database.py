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

    def get_all_signatures(self):
        self.c.execute('SELECT name FROM articles GROUP BY name')
        names = self.c.fetchall()
        return {name: self.get_signature(name) for name in names}

    # Drop article table
    def purge(self):
        self.c.execute('DROP TABLE articles')
        self.con.commit()

    def close(self):
        self.con.close()

db = Database()
# db.add_article('Test', [1,2,3,4,5])
# db.add_article('Scoop', [6,7,8,9,10])
# db.add_article('Poop', [11,12,13,14,15])
# signature = db.get_signature('Test')
signatures = db.get_all_signatures()
print(signatures)
db.close()