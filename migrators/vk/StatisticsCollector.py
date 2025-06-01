#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json


class StatisticsCollector:
    """Сборщик статистики по миграции"""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def check_migration_results(self):
        """Проверяет результаты миграции и возвращает статистику"""
        try:
            conn = sqlite3.connect(self.config.target_db_path)
            cursor = conn.cursor()

            # Проверяем количество организаций
            cursor.execute("SELECT COUNT(*) FROM orgs")
            orgs_count = cursor.fetchone()[0]

            # Проверяем количество постов
            cursor.execute("SELECT COUNT(*) FROM posts")
            posts_count = cursor.fetchone()[0]

            # Статистика по городам в организациях
            cursor.execute("SELECT COUNT(*) FROM orgs WHERE cities IS NOT NULL AND cities != '[]'")
            orgs_with_cities = cursor.fetchone()[0]

            # Статистика по городам и адресам в постах
            cursor.execute("SELECT COUNT(*) FROM posts WHERE cities IS NOT NULL AND cities != '[]'")
            posts_with_cities = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM posts WHERE address IS NOT NULL AND address != '[]'")
            posts_with_addresses = cursor.fetchone()[0]

            self.logger.log(f"\n=== ИТОГОВАЯ СТАТИСТИКА ===")
            self.logger.log(f"Всего организаций в базе: {orgs_count}")
            self.logger.log(f"  - с найденными городами: {orgs_with_cities}")
            self.logger.log(f"Всего постов в базе: {posts_count}")
            self.logger.log(f"  - с найденными городами: {posts_with_cities}")
            self.logger.log(f"  - с найденными адресами: {posts_with_addresses}")

            # Показываем примеры
            self._show_organization_examples(cursor)
            self._show_post_examples(cursor)

            # Показываем топ городов
            self._show_top_cities_in_orgs(cursor)
            self._show_top_cities_in_posts(cursor)

            conn.close()
            return orgs_count, posts_count

        except Exception as e:
            self.logger.log(f"Ошибка при проверке результатов: {str(e)}")
            return 0, 0

    def _show_organization_examples(self, cursor):
        """Показывает примеры организаций"""
        cursor.execute("SELECT id, url, descr_raw, cities FROM orgs ORDER BY id DESC LIMIT 3")
        orgs_sample = cursor.fetchall()
        if orgs_sample:
            self.logger.log(f"\nПоследние добавленные организации:")
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
                self.logger.log(f"  ID: {org[0]}, URL: {org[1]}{cities_info}", False)
                self.logger.log(f"    Описание: {descr_preview}", False)

    def _show_post_examples(self, cursor):
        """Показывает примеры постов"""
        cursor.execute("""
            SELECT p.id, p.post_id, p.post_content, p.cities, p.address, o.url 
            FROM posts p 
            LEFT JOIN orgs o ON p.org_id = o.id 
            ORDER BY p.id DESC LIMIT 3
        """)
        posts_sample = cursor.fetchall()
        if posts_sample:
            self.logger.log(f"\nПоследние добавленные посты:")
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

                self.logger.log(f"  ID: {post[0]}, Post ID: {post[1]}, Организация: {post[5]}", False)
                self.logger.log(f"    Контент: {content}", False)
                if cities_info:
                    self.logger.log(f"    {cities_info}", False)
                if addresses_info:
                    self.logger.log(f"    {addresses_info}", False)

    def _show_top_cities_in_orgs(self, cursor):
        """Показывает топ городов в организациях"""
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
            self.logger.log(f"\nТоп-{self.config.log_limit_top_cities} городов в организациях:")
            sorted_cities = sorted(city_count.items(), key=lambda x: x[1], reverse=True)[
                            :self.config.log_limit_top_cities]
            for city, count in sorted_cities:
                self.logger.log(f"  {city}: {count} упоминаний", False)

    def _show_top_cities_in_posts(self, cursor):
        """Показывает топ городов в постах"""
        cursor.execute("SELECT cities FROM posts WHERE cities IS NOT NULL AND cities != '[]'")
        post_cities_data = cursor.fetchall()

        post_city_count = {}
        for row in post_cities_data:
            try:
                cities = json.loads(row[0])
                for city in cities:
                    post_city_count[city] = post_city_count.get(city, 0) + 1
            except:
                continue

        if post_city_count:
            self.logger.log(f"\nТоп-{self.config.log_limit_top_cities} городов в постах:")
            sorted_post_cities = sorted(post_city_count.items(), key=lambda x: x[1], reverse=True)[
                                 :self.config.log_limit_top_cities]
            for city, count in sorted_post_cities:
                self.logger.log(f"  {city}: {count} упоминаний", False)

