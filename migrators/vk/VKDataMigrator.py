#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

from migrators.vk.DataMigrator import DataMigrator
from migrators.vk.DatabaseManager import DatabaseManager
from migrators.vk.EventDetector import EventDetector
from migrators.vk.StatisticsCollector import StatisticsCollector
from migrators.vk.TextAnalyzer import TextAnalyzer
from migrators.vk.VKMigratorConfig import VKMigratorConfig
from migrators.vk.VKMigratorLogger import VKMigratorLogger


class VKDataMigrator:
    """Главный класс для миграции данных VK"""

    def __init__(self, target_db_path="./db/db.db", vk_dumps_dir="./dumps/vk/"):
        self.config = VKMigratorConfig(target_db_path, vk_dumps_dir)
        self.logger = VKMigratorLogger()
        self.text_analyzer = TextAnalyzer(self.logger)
        self.db_manager = DatabaseManager(self.config, self.logger)
        self.data_migrator = DataMigrator(self.config, self.logger, self.text_analyzer)
        self.statistics = StatisticsCollector(self.config, self.logger)

    def migrate_single_db(self, vk_db_path):
        """Мигрирует данные из одного VK .db файла"""
        source_file = os.path.basename(vk_db_path)
        self.logger.log(f"\n--- Обработка файла: {source_file} ---")

        try:
            # Проверяем размер файла
            file_size = os.path.getsize(vk_db_path)
            self.logger.log(f"Размер файла: {file_size / 1024 / 1024:.2f} MB")

            # Подключаемся к VK базе
            vk_conn = sqlite3.connect(vk_db_path)
            vk_cursor = vk_conn.cursor()

            # Проверяем структуру VK базы
            if not self.db_manager.check_vk_db_structure(vk_cursor, source_file):
                vk_conn.close()
                return 0, 0

            # Подключаемся к целевой базе
            target_conn = sqlite3.connect(self.config.target_db_path)
            target_cursor = target_conn.cursor()

            # Мигрируем группы в организации
            orgs_migrated = self.data_migrator.migrate_groups_to_orgs(vk_cursor, target_cursor, source_file)

            # Мигрируем посты
            event_detector = EventDetector(self.logger)
            target_cursor = target_conn.cursor()
            posts_migrated = self.data_migrator.migrate_posts(vk_cursor, target_cursor, source_file, event_detector)

            # Сохраняем изменения
            target_conn.commit()

            # Закрываем соединения
            vk_conn.close()
            target_conn.close()

            self.logger.log(
                f"Завершена обработка {source_file}: организаций +{orgs_migrated}, постов +{posts_migrated}")
            return orgs_migrated, posts_migrated

        except Exception as e:
            self.logger.log(f"Ошибка при обработке {vk_db_path}: {str(e)}")
            return 0, 0

    def run_migration(self):
        """Запускает полную миграцию"""
        self.logger.log("=== НАЧАЛО МИГРАЦИИ VK ДАННЫХ ===")

        # Создаем целевую базу данных
        self.db_manager.create_target_database()

        # Получаем список VK файлов
        vk_files = self.db_manager.get_vk_db_files()

        if not vk_files:
            self.logger.log("Не найдено файлов VK базы данных для миграции")
            return

        total_orgs_migrated = 0
        total_posts_migrated = 0
        files_processed = 0

        # Обрабатываем каждый файл
        for vk_file in vk_files:
            orgs_migrated, posts_migrated = self.migrate_single_db(vk_file)
            total_orgs_migrated += orgs_migrated
            total_posts_migrated += posts_migrated
            files_processed += 1

        # Проверяем результаты
        final_orgs_count, final_posts_count = self.statistics.check_migration_results()

        # Сохраняем отчет
        self.logger.save_report(
            self.config.report_path,
            total_orgs_migrated,
            total_posts_migrated,
            files_processed,
            final_orgs_count,
            final_posts_count
        )

        self.logger.log(f"\n=== МИГРАЦИЯ ЗАВЕРШЕНА ===")
        self.logger.log(f"Обработано файлов: {files_processed}")
        self.logger.log(f"Добавлено организаций: {total_orgs_migrated}")
        self.logger.log(f"Добавлено постов: {total_posts_migrated}")


def main():
    """Основная функция"""
    print("=== VK DATA MIGRATOR ===")

    target_db = input("Введите путь к целевой базе данных (по умолчанию: ./db/db.db): ").strip()
    if not target_db:
        target_db = "./db/db.db"

    vk_dumps = input("Введите путь к директории с VK дампами (по умолчанию: ./dumps/vk/): ").strip()
    if not vk_dumps:
        vk_dumps = "./dumps/vk/"

    if not os.path.exists(vk_dumps):
        print(f"Ошибка: Директория не найдена: {vk_dumps}")
        return

    migrator = VKDataMigrator(target_db, vk_dumps)
    migrator.run_migration()


if __name__ == "__main__":
    main()
