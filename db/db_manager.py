import sqlite3
from sqlite3 import Error


class DB:

    def __init__(self, db_name=None):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        # TODO: add an try-except block
        self.connection = sqlite3.connect(self.db_name)

    def get_cursor(self):
        self.connect()
        self.cursor = self.connection.cursor()

    def close_connection(self):

        try:
            self.cursor.close()
        except AttributeError:
            # TODO: add logs here
            pass

        try:
            self.connection.close()
        except AttributeError:
            # TODO: add logs here
            pass

    def create_structure(self):
        self.get_cursor()

        self.cursor.executemany(
            '''
            CREATE TABLE ProfileMeta (
                profile_id INTEGER PRIMARY KEY,
                profile_name VARCHAR(64)  
            );
            
            CREATE TABLE ProfileEntries(
                entry_id INTEGER PRIMARY KEY,
                entry_name VARCHAR(128),
                executable_path TEXT,
                priority INTEGER, 
            );
            '''
        )
        self.close_connection()

    def drop(self):
        self.get_cursor()

        self.cursor.executemany(
            '''
            DROP TABLE ProfileMeta;
            DROP TABLE ProfileEntries;
            '''
        )
        self.close_connection()
