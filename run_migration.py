#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Быстрый запуск миграции VK данных
Структура проекта: wtg_admin/run_web_interface/
"""

import sys
import os

# Добавляем текущую директорию в путь для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Создаем необходимые директории если их нет
os.makedirs(os.path.join(current_dir, 'db'), exist_ok=True)
os.makedirs(os.path.join(current_dir, 'dumps', 'vk'), exist_ok=True)
os.makedirs(os.path.join(current_dir, 'logs'), exist_ok=True)
os.makedirs(os.path.join(current_dir, 'reports'), exist_ok=True)

def main():
    """Основная функция для запуска мигратора"""
    print("=== VK DATA MIGRATOR ===")

    # Пути к файлам
    target_db = os.path.join(current_dir, "db", "db.db")
    vk_dumps = os.path.join(current_dir, "dumps", "vk")

    print(f"Целевая база данных: {target_db}")
    print(f"Директория с VK дампами: {vk_dumps}")

    if not os.path.exists(vk_dumps):
        print(f"❌ Ошибка: Директория не найдена: {vk_dumps}")
        print("Создайте директорию и поместите в неё файлы .db с данными VK")
        return 1

    # Проверяем наличие .db файлов
    db_files = [f for f in os.listdir(vk_dumps) if f.endswith('.db')]
    if not db_files:
        print(f"❌ В директории {vk_dumps} не найдено .db файлов")
        print("Поместите файлы с данными VK в эту директорию")
        return 1

    print(f"✅ Найдено {len(db_files)} файлов для миграции:")
    for db_file in db_files:
        file_path = os.path.join(vk_dumps, db_file)
        file_size = os.path.getsize(file_path) / 1024 / 1024
        print(f"   - {db_file} ({file_size:.2f} MB)")

    try:
        from migrators.vk.VKDataMigrator import VKDataMigrator

        migrator = VKDataMigrator(target_db, vk_dumps)
        migrator.run_migration()

        print("\n🎉 Миграция завершена успешно!")
        print("💡 Теперь можете запустить веб-интерфейс: python run_web_interface.py")
        return 0

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что папка migrators/ находится в текущей директории")
        return 1
    except Exception as e:
        print(f"❌ Ошибка при миграции: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)