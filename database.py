import sqlite3
import time

class Database:
    def __init__(self, db_name='trumpi_pumpi.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (chat_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, energy INTEGER DEFAULT 1000, 
                      max_energy INTEGER DEFAULT 1000, tap_power INTEGER DEFAULT 1, last_energy_update INTEGER)''')
        conn.commit()
        conn.close()

    def register_user(self, chat_id, ref_id=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users (chat_id, last_energy_update) VALUES (?, ?)', 
                  (chat_id, int(time.time())))
        if ref_id:
            c.execute('UPDATE users SET balance = balance + 100 WHERE chat_id = ?', (int(ref_id),))
        conn.commit()
        conn.close()

    def tap(self, chat_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT balance, energy, tap_power FROM users WHERE chat_id = ?', (chat_id,))
        balance, energy, tap_power = c.fetchone()
        
        if energy >= 1:
            energy -= 1
            balance += tap_power
            c.execute('UPDATE users SET balance = ?, energy = ? WHERE chat_id = ?', 
                      (balance, energy, chat_id))
        
        conn.commit()
        conn.close()
        return balance, energy

    def get_stats(self, chat_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT balance, energy, max_energy FROM users WHERE chat_id = ?', (chat_id,))
        result = c.fetchone()
        conn.close()
        return result if result else (0, 1000, 1000)
