#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Удобный скрипт для запуска VK мигратора
"""

import os
import sys

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from migrators.vk.VKDataMigrator import VKDataMigrator


def main():
    """Основная функция для запуска мигратора"""
    print("=== VK DATA MIGRATOR ===")

    # Используем значения по умолчанию для автоматического запуска
    target_db = "./db/db.db"
    vk_dumps = "./dumps/vk/"

    print(f"Целевая база данных: {target_db}")
    print(f"Директория с VK дампами: {vk_dumps}")

    if not os.path.exists(vk_dumps):
        print(f"Ошибка: Директория не найдена: {vk_dumps}")
        print("Создайте директорию и поместите в неё файлы .db с данными VK")
        return

    migrator = VKDataMigrator()
    migrator.run_migration()


if __name__ == "__main__":
    main()
