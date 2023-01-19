import sqlite3
import os


class DBSetup:
    @staticmethod
    def initialize_db(cur):
        cur.execute('''CREATE TABLE IF NOT EXISTS user_details
            (id TEXT PRIMARY KEY, 
            password TEXT NOT NULL,
            username TEXT NOT NULL,
            class TEXT NOT NULL);
        ''')

    def __init__(self, db_path):
        self.db_path = db_path
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        self.initialize_db(c)
        conn.commit()

    def exists(self, login, password):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f'SELECT * FROM user_details WHERE id = "{login}" AND password = "{password}";')
        return c.fetchone() is not None

    def add_user(self, login, password, username, section):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Check if username already exists
        c.execute(f'SELECT * FROM user_details WHERE login = "{login}";')
        if c.fetchone() is not None:
            c.execute(f'UPDATE user_details SET password = "{password}", username = "{username}", class = "{section}" WHERE id = "{login}";')
        c.execute(f'INSERT INTO user_details VALUES ("{login}", "{password}", "{username}", "{section}");')
        conn.commit()

# my_db = DBSetup('my_db.db')
# print(my_db.exists('abrehman.bscs21seecs', 'K2Cr2O7**'))