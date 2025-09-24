import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Tuple


class Database:
    def __init__(self, db_path: str = "data/users.db"):
        # Создаем папку data, если её нет
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Создание таблицы пользователей при запуске"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT,
                username TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица расходов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                category1 TEXT,
                amount1 REAL,
                category2 TEXT,
                amount2 REAL,
                category3 TEXT,
                amount3 REAL,
                record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
            )
        ''')

        conn.commit()
        conn.close()

    def user_exists(self, telegram_id: int) -> bool:
        """Проверка, существует ли пользователь"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()

        conn.close()
        return result is not None

    def register_user(self, telegram_id: int, first_name: str, last_name: str = None, username: str = None) -> bool:
        """Регистрация нового пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO users (telegram_id, first_name, last_name, username)
                VALUES (?, ?, ?, ?)
            ''', (telegram_id, first_name, last_name, username))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Пользователь уже существует
            return False

    def get_user(self, telegram_id: int) -> Optional[dict]:
        """Получение информации о пользователе"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT telegram_id, first_name, last_name, username, registration_date
            FROM users WHERE telegram_id = ?
        ''', (telegram_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'telegram_id': result[0],
                'first_name': result[1],
                'last_name': result[2],
                'username': result[3],
                'registration_date': result[4]
            }
        return None

    def save_expenses(self, telegram_id: int, category1: str, amount1: float,
                      category2: str, amount2: float, category3: str, amount3: float) -> bool:
        """Сохранение расходов пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO expenses (telegram_id, category1, amount1, category2, amount2, category3, amount3)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (telegram_id, category1, amount1, category2, amount2, category3, amount3))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении расходов: {e}")
            return False

    def get_latest_expenses(self, telegram_id: int) -> Optional[dict]:
        """Получение последних расходов пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT category1, amount1, category2, amount2, category3, amount3, record_date
                FROM expenses 
                WHERE telegram_id = ?
                ORDER BY record_date DESC
                LIMIT 1
            ''', (telegram_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'category1': result[0],
                    'amount1': result[1],
                    'category2': result[2],
                    'amount2': result[3],
                    'category3': result[4],
                    'amount3': result[5],
                    'date': result[6]
                }
            return None
        except Exception as e:
            print(f"Ошибка при получении расходов: {e}")
            return None