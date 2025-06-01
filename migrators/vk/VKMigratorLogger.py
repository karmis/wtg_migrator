#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime


class VKMigratorLogger:
    """Логгер для VK мигратора"""

    def __init__(self):
        self.log_messages = []

    def log(self, message, print_message=True):
        """Добавляет сообщение в лог"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)

        if print_message:
            print(message)

    def save_report(self, report_path, total_orgs_migrated, total_posts_migrated,
                    files_processed, final_orgs_count, final_posts_count):
        """Сохраняет подробный отчет о миграции"""
        try:
            import os
            os.makedirs(os.path.dirname(report_path), exist_ok=True)

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=== ОТЧЕТ О МИГРАЦИИ VK ДАННЫХ ===\n")
                f.write(f"Дата миграции: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                # f.write(f"Natasha анализ: {'включен' if natasha_enabled else 'отключен'}\n\n")

                f.write("=== РЕЗУЛЬТАТЫ ===\n")
                f.write(f"Обработано файлов: {files_processed}\n")
                f.write(f"Добавлено организаций: {total_orgs_migrated}\n")
                f.write(f"Добавлено постов: {total_posts_migrated}\n")
                f.write(f"Итого организаций в базе: {final_orgs_count}\n")
                f.write(f"Итого постов в базе: {final_posts_count}\n\n")

                f.write("=== ПОДРОБНЫЙ ЛОГ ===\n")
                for message in self.log_messages:
                    f.write(message + "\n")

            self.log(f"Отчет сохранен: {report_path}")

        except Exception as e:
            self.log(f"Ошибка при сохранении отчета: {str(e)}")
