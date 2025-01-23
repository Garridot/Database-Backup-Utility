import sqlite3
from sqlite3 import Error

class SQLiteConnector:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except Error as e:
            print(f"Error connecting to SQLite database: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()