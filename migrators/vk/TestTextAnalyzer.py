#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестирование TextAnalyzer
"""

import sys
import os

from migrators.vk.VKMigratorLogger import VKMigratorLogger

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from migrators.vk.TextAnalyzer import TextAnalyzer



def test_text_analyzer():
    """Тестирует работу анализатора текста"""

    logger = VKMigratorLogger()
    analyzer = TextAnalyzer(logger)

    # Тестовые тексты
    test_texts = [
        "Приглашаем на мероприятие в Москве, ул. Тверская, д. 10",
        "Наш офис находится в г. Санкт-Петербург, Невский проспект, 25",
        "Филиалы в Екатеринбурге, Новосибирске и Казани",
        "Работаем в СПб, Питере и Мск",
        "Адрес: 123456, Московская область, г. Подольск, ул. Ленина, д. 5, кв. 10",
        "Встреча состоится в Нижнем Новгороде на пл. Минина",
        "Доставка по всей России: Краснодар, Ростов-на-Дону, Волгоград",
        "Контакты: Тюмень, микрорайон Восточный, д. 15",
        "Приезжайте к нам в Красноярск!",
        "Офис в центре Воронежа, рядом с театром"
    ]

    print("=== ТЕСТИРОВАНИЕ TEXT ANALYZER ===\n")

    # Показываем статистику анализатора
    stats = analyzer.get_statistics()
    print("Статистика анализатора:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    # Тестируем каждый текст
    for i, text in enumerate(test_texts, 1):
        print(f"Тест {i}:")
        print(f"Текст: {text}")

        result = analyzer.analyze_text_detailed(text)

        print(f"Найденные города: {result['cities']}")
        print(f"Найденные адреса: {result['addresses']}")
        print(f"Информация: {result['analysis_info']}")
        print("-" * 50)

    # Тест производительности
    print("\n=== ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ===")
    import time

    long_text = " ".join(test_texts * 100)  # Длинный текст

    start_time = time.time()
    cities, addresses = analyzer.extract_locations_and_addresses(long_text)
    end_time = time.time()

    print(f"Обработка текста длиной {len(long_text)} символов:")
    print(f"Время обработки: {end_time - start_time:.4f} секунд")
    print(f"Найдено городов: {len(cities)}")
    print(f"Найдено адресов: {len(addresses)}")


if __name__ == "__main__":
    test_text_analyzer()
