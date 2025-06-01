#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


class VKMigratorConfig:
    """Конфигурация для VK мигратора"""

    def __init__(self, target_db_path="./db/db.db", vk_dumps_dir="./dumps/vk/"):
        self.target_db_path = target_db_path
        self.vk_dumps_dir = vk_dumps_dir

        # Создаем имя файла отчета с постфиксом
        db_name = os.path.splitext(os.path.basename(target_db_path))[0]
        self.report_path = os.path.join(os.path.dirname(target_db_path), f"migration_report.vk.{db_name}.txt")

        # Настройки логирования
        self.log_limit_examples = 5  # Сколько примеров показывать в логах
        self.log_limit_top_cities = 10  # Сколько топ городов показывать
