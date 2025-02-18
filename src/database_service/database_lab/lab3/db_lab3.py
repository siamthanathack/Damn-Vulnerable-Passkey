# This project was developed by Siam Thanat Hack Co., Ltd. (STH).
# Website: https://sth.sh  
# Contact: pentest@sth.sh
import sqlite3

from database_service.database_lab.lab3 import DATABASE3
import base64

def get_db_connection():
    conn = sqlite3.connect(DATABASE3, timeout=10, check_same_thread=False)
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
        conn.execute("DROP TABLE IF EXISTS privatekeys")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS privatekeys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                raw_id BLOB NOT NULL,
                private_key BLOB NOT NULL,
                counter INT NOT NULL
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
        conn.execute("DROP TABLE IF EXISTS users")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
            )
        ''')

        conn.execute('''
            INSERT INTO users (username) VALUES ("admin")
        ''')

        private_key_text = '{"d": "CEA7DF21EC436AECDED661B4D8019983223B9C6B3F27D6C2207D266D9B891B1A", "curve": "ED25519", "x": "56B42D6D5038879D6C8764B9D8A47277F685F71A4E050131E7C9B6E856327C1C", "keyType": "OKP", "algorithm": "EdDSA"}'
        conn.execute('''
            INSERT INTO privatekeys (username, raw_id, private_key, counter) 
            VALUES ("admin", ?, ?, ?)
        ''', ("", private_key_text, 0))

        public_key_text = 'pQEBAycgBiFYIFa0LW1QOIedbIdkudikcnf2hfcaTgUBMefJtuhWMnwcI1ggzqffIexDauze1mG02AGZgyI7nGs_J9bCIH0mbZuJGxo'
        padded1_base64 = public_key_text + "=" * (-len(public_key_text) % 4)
        public1_key_text = base64.urlsafe_b64decode(padded1_base64)


        raw_id_base64 = "CZIYpJXqT18cJcjo0KV096LSRX15vQ4gKtE3HU_93bE"
        padded_base64 = raw_id_base64 + "=" * (-len(raw_id_base64) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded_base64)

        conn.execute('''
            INSERT INTO pubkeys (username, raw_id, public_key, counter) 
            VALUES ("admin", ?, ?, ?)
        ''', (decoded_bytes, public1_key_text, 0))

        conn.commit()
