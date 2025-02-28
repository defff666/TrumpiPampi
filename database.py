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
                          max_energy INTEGER DEFAULT 1000, tap_power INTEGER DEFAULT 1, last_energy_update INTEGER)''')
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
            c.execute('INSERT OR IGNORE INTO users (chat_id, last_energy_update) VALUES (?, ?)', 
                      (chat_id, int(time.time())))
            if ref_id:
                c.execute('UPDATE users SET balance = balance + 100 WHERE chat_id = ?', (int(ref_id),))
            conn.commit()
            logger.info(f"User {chat_id} registered with ref_id: {ref_id}")
        except Exception as e:
            logger.error(f"Error registering user {chat_id}: {e}")
        finally:
            conn.close()

    def tap(self, chat_id):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('SELECT balance, energy, tap_power FROM users WHERE chat_id = ?', (chat_id,))
            result = c.fetchone()
            if result:
                balance, energy, tap_power = result
            else:
                logger.warning(f"User {chat_id} not found, initializing...")
                self.register_user(chat_id)
                balance, energy, tap_power = 0, 1000, 1
            
            if energy >= 1:
                energy -= 1
                balance += tap_power
                c.execute('UPDATE users SET balance = ?, energy = ? WHERE chat_id = ?', 
                          (balance, energy, chat_id))
                conn.commit()
                logger.info(f"Tap successful for {chat_id}: new balance={balance}, energy={energy}")
            else:
                logger.warning(f"Tap failed for {chat_id}: not enough energy")
            return balance, energy
        except Exception as e:
            logger.error(f"Error processing tap for {chat_id}: {e}")
            return 0, 1000  # Возвращаем дефолт на случай ошибки
        finally:
            conn.close()

    def get_stats(self, chat_id):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('SELECT balance, energy, max_energy FROM users WHERE chat_id = ?', (chat_id,))
            result = c.fetchone()
            if result:
                return result
            logger.warning(f"Stats not found for {chat_id}, returning defaults")
            return 0, 1000, 1000
        except Exception as e:
            logger.error(f"Error getting stats for {chat_id}: {e}")
            return 0, 1000, 1000
        finally:
            conn.close()
