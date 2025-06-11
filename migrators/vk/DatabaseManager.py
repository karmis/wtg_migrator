#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import glob


class DatabaseManager:
    """Менеджер базы данных для VK мигратора"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def get_vk_db_files(self):
        """Получает список всех .db файлов в директории dumps/vk/"""
        pattern = os.path.join(self.config.vk_dumps_dir, "*.db")
        files = glob.glob(pattern)
        self.logger.log(f"Найдено {len(files)} файлов VK базы данных в {self.config.vk_dumps_dir}")
        for file in files:
            self.logger.log(f"  - {file}", False)
        return files

    def create_target_database(self):
        """Создает целевую базу данных с необходимыми таблицами"""
        # Создаем директорию если её нет
        os.makedirs(os.path.dirname(self.config.target_db_path), exist_ok=True)

        conn = sqlite3.connect(self.config.target_db_path)
        cursor = conn.cursor()

        # Создаем таблицу orgs с полем cities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orgs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                descr_raw TEXT,
                last_checked_date TEXT,
                last_post_date TEXT,
                last_event_date TEXT,
                descr TEXT,
                cities TEXT
            )
        """)

        # Создаем таблицу posts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id INTEGER,
                post_content TEXT,
                content TEXT,
                post_date TEXT,
                post_likes INTEGER,
                post_comments INTEGER,
                post_reposts INTEGER,
                post_images TEXT,
                images TEXT,
                url TEXT,
                post_id TEXT,
                cities TEXT,
                address TEXT,
                maybe_event BOOLEAN,
                is_published BOOLEAN DEFAULT 1,
                FOREIGN KEY(org_id) REFERENCES orgs(id)
            )
        """)

        # Добавляем столбцы если они не существуют (для обратной совместимости)
        self._add_columns_if_not_exist(cursor)

        conn.commit()
        conn.close()
        self.logger.log(f"Целевая база данных создана/проверена: {self.config.target_db_path}")

    def _add_columns_if_not_exist(self, cursor):
        """Добавляет столбцы если они не существуют"""
        try:
            cursor.execute("ALTER TABLE orgs ADD COLUMN cities TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE posts ADD COLUMN cities TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE posts ADD COLUMN address TEXT")
        except sqlite3.OperationalError:
            pass

    def check_vk_db_structure(self, vk_cursor, source_file):
        """Проверяет структуру VK базы данных"""
        vk_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in vk_cursor.fetchall()]
        self.logger.log(f"Таблицы в файле: {', '.join(tables)}", False)

        if 'vk_groups' not in tables or 'vk_posts' not in tables:
            self.logger.log(f"Пропускаем {source_file} - отсутствуют необходимые таблицы")
            return False

        return True
