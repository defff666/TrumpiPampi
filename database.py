import sqlite3
import time
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
                          last_update REAL DEFAULT 0)''')
            c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                         (task_id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, description TEXT, 
                          reward INTEGER, completed INTEGER DEFAULT 0)''')
            conn.commit()
        logger.info("Database initialized successfully")

    def register_user(self, chat_id, ref_id=None):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO users (chat_id, last_update) VALUES (?, ?)', (chat_id, time.time()))
            if ref_id:
                c.execute('UPDATE users SET balance = balance + 100 WHERE chat_id = ?', (int(ref_id),))
                c.execute('UPDATE users SET last_update = ? WHERE chat_id = ?', (time.time(), int(ref_id)))
            # Начальные таски
            c.execute('INSERT OR IGNORE INTO tasks (chat_id, description, reward) VALUES (?, ?, ?)', 
                      (chat_id, "Make 100 taps", 500))
            c.execute('INSERT OR IGNORE INTO tasks (chat_id, description, reward) VALUES (?, ?, ?)', 
                      (chat_id, "Invite 1 friend", 1000))
            conn.commit()
        logger.info(f"User {chat_id} registered with ref_id: {ref_id}")

    def sync_user(self, chat_id, balance, energy, max_energy, level, multitap, last_update):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO users (chat_id, balance, energy, max_energy, level, multitap, last_update) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                      (chat_id, balance, energy, max_energy, level, multitap, last_update))
            conn.commit()
        logger.info(f"User {chat_id} synced: balance={balance}, energy={energy}, max_energy={max_energy}, level={level}, multitap={multitap}")

    def get_stats(self, chat_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('SELECT balance, energy, max_energy, level, multitap, last_update FROM users WHERE chat_id = ?', (chat_id,))
            result = c.fetchone()
            if result:
                balance, energy, max_energy, level, multitap, last_update = result
                elapsed = time.time() - last_update
                recovery_rate = level
                energy = min(max_energy, energy + int(elapsed * recovery_rate))
                c.execute('UPDATE users SET energy = ?, last_update = ? WHERE chat_id = ?', (energy, time.time(), chat_id))
                conn.commit()
                return {'balance': balance, 'energy': energy, 'max_energy': max_energy, 'level': level, 'multitap': multitap}
            self.register_user(chat_id)  # Регистрируем, если не найден
            return self.get_stats(chat_id)

    def get_tasks(self, chat_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('SELECT task_id, description, reward, completed FROM tasks WHERE chat_id = ?', (chat_id,))
            return [{'id': row[0], 'description': row[1], 'reward': row[2], 'completed': bool(row[3])} for row in c.fetchall()]

    def complete_task(self, chat_id, task_id):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('SELECT reward, completed FROM tasks WHERE chat_id = ? AND task_id = ?', (chat_id, task_id))
            result = c.fetchone()
            if result and not result[1]:
                reward = result[0]
                c.execute('UPDATE tasks SET completed = 1 WHERE chat_id = ? AND task_id = ?', (chat_id, task_id))
                c.execute('UPDATE users SET balance = balance + ? WHERE chat_id = ?', (reward, chat_id))
                conn.commit()
                return reward
            return 0
