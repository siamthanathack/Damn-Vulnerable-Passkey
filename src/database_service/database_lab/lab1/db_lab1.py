# This project was developed by Siam Thanat Hack Co., Ltd. (STH).
# Website: https://sth.sh  
# Contact: pentest@sth.sh
import sqlite3

from database_service.database_lab.lab1 import DATABASE1

def get_db_connection():
    conn = sqlite3.connect(DATABASE1, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS challenges")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                challenge TEXT NOT NULL
            )
        ''')
        conn.execute("DROP TABLE IF EXISTS pubkeys")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pubkeys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                raw_id BLOB NOT NULL,
                public_key BLOB NOT NULL,
                counter INT NOT NULL
            )
        ''')
        conn.commit()
