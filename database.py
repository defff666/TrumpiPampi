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
                          max_energy INTEGER DEFAULT 1000, tap_power INTEGER DEFAULT 1, last_energy_update INTEGER, 
                          level INTEGER DEFAULT 1, multitap INTEGER DEFAULT 1)''')
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
            c.execute('SELECT balance, energy, tap_power, max_energy, level, multitap, last_energy_update FROM users WHERE chat_id = ?', (chat_id,))
            result = c.fetchone()
            if result:
                balance, energy, tap_power, max_energy, level, multitap, last_update = result
            else:
                logger.warning(f"User {chat_id} not found, initializing...")
                self.register_user(chat_id)
                balance, energy, tap_power, max_energy, level, multitap, last_update = 0, 1000, 1, 1000, 1, 1, int(time.time())

            # Восстановление энергии
            current_time = int(time.time())
            elapsed = current_time - last_update
            energy恢复 = elapsed * level  # 1 энергия/сек на 1 уровне, 2/сек на 2 уровне и т.д.
            energy = min(max_energy, energy + energy恢复)

            if energy >= multitap:
                energy -= multitap
                balance += multitap
                # Проверка уровня
                new_level = 1 + (balance // 1000)
                if new_level > level:
                    level = new_level
                    max_energy = 1000 * level
                    multitap = level
                    logger.info(f"User {chat_id} leveled up to {level}, max_energy={max_energy}, multitap={multitap}")
                c.execute('UPDATE users SET balance=?, energy=?, level=?, max_energy=?, multitap=?, last_energy_update=? WHERE chat_id=?', 
                          (balance, energy, level, max_energy, multitap, current_time, chat_id))
                conn.commit()
                logger.info(f"Tap successful for {chat_id}: balance={balance}, energy={energy}")
            else:
                logger.warning(f"Tap failed for {chat_id}: not enough energy")
            return balance, energy
        except Exception as e:
            logger.error(f"Error processing tap for {chat_id}: {e}")
            return 0, 1000
        finally:
            conn.close()

    def get_stats(self, chat_id):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('SELECT balance, energy, max_energy, level, multitap, last_energy_update FROM users WHERE chat_id = ?', (chat_id,))
            result = c.fetchone()
            if result:
                balance, energy, max_energy, level, multitap, last_update = result
                # Восстановление энергии
                current_time = int(time.time())
                elapsed = current_time - last_update
                energy恢复 = elapsed * level
                energy = min(max_energy, energy + energy恢复)
                c.execute('UPDATE users SET energy=?, last_energy_update=? WHERE chat_id=?', 
                          (energy, current_time, chat_id))
                conn.commit()
                return balance, energy, max_energy, level, multitap
            logger.warning(f"Stats not found for {chat_id}, returning defaults")
            return 0, 1000, 1000, 1, 1
        except Exception as e:
            logger.error(f"Error getting stats for {chat_id}: {e}")
            return 0, 1000, 1000, 1, 1
        finally:
            conn.close()
