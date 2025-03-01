import sqlite3
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name='trumpi_pumpi.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users 
                         (chat_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, energy INTEGER DEFAULT 1000, 
                          max_energy INTEGER DEFAULT 1000, level INTEGER DEFAULT 1, multitap INTEGER DEFAULT 1,
                          last_sync INTEGER DEFAULT 0)''')  # Добавляем last_sync
            conn.commit()
        logger.info("Database initialized successfully")

    def register_user(self, chat_id, ref_id=None):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO users (chat_id, last_sync) VALUES (?, ?)', (chat_id, int(time.time())))
            if ref_id:
                c.execute('UPDATE users SET balance = balance + 100 WHERE chat_id = ?', (int(ref_id),))
            conn.commit()
        logger.info(f"User {chat_id} registered with ref_id: {ref_id}")

    def sync_user(self, chat_id, balance, energy, max_energy, level, multitap):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO users (chat_id, balance, energy, max_energy, level, multitap, last_sync) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                      (chat_id, balance, energy, max_energy, level, multitap, int(time.time())))
            conn.commit()
        logger.info(f"User {chat_id} synced: balance={balance}, energy={energy}, max_energy={max_energy}, level={level}, multitap={multitap}")

    def get_stats(self, chat_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('SELECT balance, energy, max_energy, level, multitap, last_sync FROM users WHERE chat_id = ?', (chat_id,))
            result = c.fetchone()
            if result:
                balance, energy, max_energy, level, multitap, last_sync = result
                # Восстановление энергии оффлайн
                elapsed = int(time.time()) - last_sync
                recovery_rate = level  # 1 энергия/сек на 1 уровне
                energy = min(max_energy, energy + elapsed * recovery_rate)
                c.execute('UPDATE users SET energy = ?, last_sync = ? WHERE chat_id = ?', (energy, int(time.time()), chat_id))
                conn.commit()
                return {'balance': balance, 'energy': energy, 'max_energy': max_energy, 'level': level, 'multitap': multitap}
            logger.info(f"Stats not found for {chat_id}, returning defaults")
            return {'balance': 0, 'energy': 1000, 'max_energy': 1000, 'level': 1, 'multitap': 1}
