import aiosqlite
import random
import os

DB_NAME = 'shop_database.db'

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                support_id TEXT UNIQUE,
                deals_count INTEGER DEFAULT 0
            )
        ''')
        # Таблица заказов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_name TEXT,
                quantity INTEGER,
                amount REAL,
                status TEXT DEFAULT 'pending'
            )
        ''')
        await db.commit()

async def get_user(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
            return await cursor.fetchone()

async def add_user(telegram_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        # Генерация уникального support_id
        while True:
            support_id = f"#{random.randint(111111, 999999)}"
            async with db.execute('SELECT 1 FROM users WHERE support_id = ?', (support_id,)) as cursor:
                if not await cursor.fetchone():
                    break
        
        await db.execute(
            'INSERT OR IGNORE INTO users (telegram_id, username, support_id) VALUES (?, ?, ?)',
            (telegram_id, username, support_id)
        )
        await db.commit()
        return support_id

async def create_order(telegram_id, item_name, quantity, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'INSERT INTO orders (user_id, item_name, quantity, amount) VALUES (?, ?, ?, ?)',
            (telegram_id, item_name, quantity, amount)
        )
        await db.commit()
        return cursor.lastrowid # Возвращаем номер сделки (ID заказа)

async def get_order(order_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM orders WHERE id = ?', (order_id,)) as cursor:
            return await cursor.fetchone()

async def update_order_status(order_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        await db.commit()

async def increment_user_deals(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET deals_count = deals_count + 1 WHERE telegram_id = ?', (telegram_id,))
        await db.commit()