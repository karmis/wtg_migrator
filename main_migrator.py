#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys


def run_vk_migrator():
    """Запускает VK мигратор"""
    print("=== ЗАПУСК VK МИГРАТОРА ===")
    try:
        result = subprocess.run([sys.executable, os.path.join("migrators", "vk", "VKDataMigrator.py")],
                              capture_output=True, text=True, encoding='utf-8')

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        if result.returncode == 0:
            print("VK миграция завершена успешно")
        else:
            print(f"VK миграция завершена с ошибкой (код: {result.returncode})")

    except Exception as e:
        print(f"Ошибка при запуске VK мигратора: {str(e)}")


def show_database_stats():
    """Показывает статистику базы данных"""
    db_path = "./db/db.db"

    if not os.path.exists(db_path):
        print("База данных не найдена. Сначала выполните миграцию.")
        return

    try:
        import sqlite3
        import json

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n=== СТАТИСТИКА БАЗЫ ДАННЫХ ===")

        # Количество организаций
        cursor.execute("SELECT COUNT(*) FROM orgs")
        orgs_count = cursor.fetchone()[0]
        print(f"Всего организаций: {orgs_count}")

        # Количество постов
        cursor.execute("SELECT COUNT(*) FROM posts")
        posts_count = cursor.fetchone()[0]
        print(f"Всего постов: {posts_count}")

        # Организации с городами
        cursor.execute("SELECT COUNT(*) FROM orgs WHERE cities IS NOT NULL AND cities != '[]'")
        orgs_with_cities = cursor.fetchone()[0]
        print(f"Организации с найденными городами: {orgs_with_cities}")

        # Посты с городами
        cursor.execute("SELECT COUNT(*) FROM posts WHERE cities IS NOT NULL AND cities != '[]'")
        posts_with_cities = cursor.fetchone()[0]
        print(f"Посты с найденными городами: {posts_with_cities}")

        # Посты с адресами
        cursor.execute("SELECT COUNT(*) FROM posts WHERE address IS NOT NULL AND address != '[]'")
        posts_with_addresses = cursor.fetchone()[0]
        print(f"Посты с найденными адресами: {posts_with_addresses}")

        # Топ городов
        cursor.execute("SELECT cities FROM orgs WHERE cities IS NOT NULL AND cities != '[]'")
        org_cities_data = cursor.fetchall()

        city_count = {}
        for row in org_cities_data:
            try:
                cities = json.loads(row[0])
                for city in cities:
                    city_count[city] = city_count.get(city, 0) + 1
            except:
                continue

        if city_count:
            print("\nТоп-10 городов в организациях:")
            sorted_cities = sorted(city_count.items(), key=lambda x: x[1], reverse=True)[:10]
            for city, count in sorted_cities:
                print(f"  {city}: {count} упоминаний")

        conn.close()

    except Exception as e:
        print(f"Ошибка при получении статистики: {str(e)}")


def check_migration_results():
    """Проверяет результаты миграции"""
    print("=== ПРОВЕРКА РЕЗУЛЬТАТОВ МИГРАЦИИ ===")

    db_path = "./db/db.db"

    if not os.path.exists(db_path):
        print("База данных не найдена. Сначала выполните миграцию.")
        return

    try:
        import sqlite3
        import json

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Проверяем количество организаций
        cursor.execute("SELECT COUNT(*) FROM orgs")
        orgs_count = cursor.fetchone()[0]
        print(f"Количество организаций в базе: {orgs_count}")

        # Проверяем количество постов
        cursor.execute("SELECT COUNT(*) FROM posts")
        posts_count = cursor.fetchone()[0]
        print(f"Количество постов в базе: {posts_count}")

        # Показываем примеры организаций
        cursor.execute("SELECT id, url, descr_raw, cities FROM orgs LIMIT 5")
        orgs_sample = cursor.fetchall()
        print("\nПримеры организаций:")
        for org in orgs_sample:
            descr_preview = org[2][:50] + "..." if org[2] and len(org[2]) > 50 else (org[2] or "Нет описания")
            cities_info = ""
            if org[3] and org[3] != "[]":
                try:
                    cities = json.loads(org[3])
                    if cities:
                        cities_info = f" [Города: {', '.join(cities)}]"
                except:
                    pass
            print(f"  ID: {org[0]}, URL: {org[1]}{cities_info}")
            print(f"    Описание: {descr_preview}")

        # Показываем примеры постов
        cursor.execute("""
            SELECT p.id, p.post_id, p.post_content, p.cities, p.address, o.url 
            FROM posts p 
            LEFT JOIN orgs o ON p.org_id = o.id 
            LIMIT 5
        """)
        posts_sample = cursor.fetchall()
        print("\nПримеры постов:")
        for post in posts_sample:
            content = post[2][:50] + "..." if post[2] and len(post[2]) > 50 else (post[2] or "Нет контента")

            cities_info = ""
            if post[3] and post[3] != "[]":
                try:
                    cities = json.loads(post[3])
                    if cities:
                        cities_info = f" [Города: {', '.join(cities)}]"
                except:
                    pass

            addresses_info = ""
            if post[4] and post[4] != "[]":
                try:
                    addresses = json.loads(post[4])
                    if addresses:
                        addresses_info = f" [Адреса: {', '.join(addresses)}]"
                except:
                    pass

            print(f"  ID: {post[0]}, Post ID: {post[1]}, Организация: {post[5]}")
            print(f"    Контент: {content}")
            if cities_info:
                print(f"    {cities_info}")
            if addresses_info:
                print(f"    {addresses_info}")

        conn.close()

    except Exception as e:
        print(f"Ошибка при проверке базы данных: {str(e)}")


def show_menu():
    """Показывает главное меню"""
    print("\n" + "="*50)
    print("           ГЛАВНЫЙ МИГРАТОР")
    print("="*50)
    print("1. Запустить VK мигратор (с анализом городов и адресов)")
    print("2. Показать статистику базы данных")
    print("3. Проверить результаты миграции")
    print("0. Выход")
    print("="*50)

    choice = input("Выберите опцию: ").strip()
    return choice


def main():
    """Основная функция"""
    while True:
        choice = show_menu()

        if choice == "1":
            run_vk_migrator()
        elif choice == "2":
            show_database_stats()
        elif choice == "3":
            check_migration_results()
        elif choice == "0":
            print("Выход из программы")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()
