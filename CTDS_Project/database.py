import sqlite3 as sql
import os
from signatures import * # pylint: disable=W0614


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

    def populate_table(self):
        self.purge()
        path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(path, 'Wikipages')
        files = os.listdir(data_path)
        for file in files:
            f = os.path.join(data_path, file)
            sig = Signatures(f).getSignatures()
            print('Adding', file, 'to database')
            self.add_article(file, sig)

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
        self.__init__()

    def close(self):
        self.con.close()


if __name__=='__main__':
    db = Database()
    # db.populate_table()
    signatures = db.get_all_signatures()
    db.close()
