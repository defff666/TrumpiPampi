import sqlite3
import time
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name='trumpi_pumpi.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users 
                         (chat_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, energy INTEGER DEFAULT 1000, 
                          max_energy INTEGER DEFAULT 1000, level INTEGER DEFAULT 1, multitap INTEGER DEFAULT 1)''')
            conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
        finally:
            conn.close()

    def register_user(self, chat_id, ref_id=None):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO users (chat_id) VALUES (?)', (chat_id,))
            if ref_id:
                c.execute('UPDATE users SET balance = balance + 100 WHERE chat_id = ?', (int(ref_id),))
            conn.commit()
            logger.info(f"User {chat_id} registered with ref_id: {ref_id}")
        except Exception as e:
            logger.error(f"Error registering user {chat_id}: {e}")
        finally:
            conn.close()

    def sync_user(self, chat_id, balance, energy, max_energy, level, multitap):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO users (chat_id, balance, energy, max_energy, level, multitap) VALUES (?, ?, ?, ?, ?, ?)', 
                      (chat_id, balance, energy, max_energy, level, multitap))
            conn.commit()
            logger.info(f"User {chat_id} synced: balance={balance}, energy={energy}, max_energy={max_energy}, level={level}, multitap={multitap}")
        except Exception as e:
            logger.error(f"Error syncing user {chat_id}: {e}")
        finally:
            conn.close()

    def get_stats(self, chat_id):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('SELECT balance, energy, max_energy, level, multitap FROM users WHERE chat_id = ?', (chat_id,))
            result = c.fetchone()
            if result:
                return {'balance': result[0], 'energy': result[1], 'max_energy': result[2], 'level': result[3], 'multitap': result[4]}
            logger.warning(f"Stats not found for {chat_id}, returning defaults")
            return {'balance': 0, 'energy': 1000, 'max_energy': 1000, 'level': 1, 'multitap': 1}
        except Exception as e:
            logger.error(f"Error getting stats for {chat_id}: {e}")
            return {'balance': 0, 'energy': 1000, 'max_energy': 1000, 'level': 1, 'multitap': 1}
        finally:
            conn.close()
