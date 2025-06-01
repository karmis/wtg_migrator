#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json

from migrators.cities import get_all_cities, get_city_aliases, normalize_city_name


class TextAnalyzer:
    """Анализатор текста для извлечения городов и адресов"""

    def __init__(self, logger):
        self.logger = logger
        self.cities_list = get_all_cities()
        self.city_aliases = get_city_aliases()

        # Создаем паттерны для поиска городов
        self._prepare_city_patterns()

        # Паттерны для поиска адресов
        self._prepare_address_patterns()

        self.logger.log(f"TextAnalyzer инициализирован с {len(self.cities_list)} городами")

    def _prepare_city_patterns(self):
        """Подготавливает регулярные выражения для поиска городов"""
        # Объединяем основные города и альтернативные названия
        all_city_names = set(self.cities_list + list(self.city_aliases.keys()))

        # Сортируем по длине (длинные названия первыми, чтобы избежать частичных совпадений)
        sorted_cities = sorted(all_city_names, key=len, reverse=True)

        # Экранируем специальные символы в названиях городов
        escaped_cities = [re.escape(city) for city in sorted_cities]

        # Создаем паттерн для поиска городов
        cities_pattern = '|'.join(escaped_cities)

        # Паттерны для различных контекстов упоминания городов
        # Паттерны для различных контекстов упоминания городов
        self.city_patterns = [
            # Прямое упоминание города
            rf'\b(?:г\.?\s*)?({cities_pattern})\b',
            # Город с предлогами
            rf'\b(?:в|из|до|от|по|на|под|над|при|около|возле|рядом\s+с)\s+(?:г\.?\s*)?({cities_pattern})\b',
            # Город в контексте адреса
            rf'\b(?:город|гор\.)\s+({cities_pattern})\b',
            # Город с областью/краем/республикой
            rf'\b({cities_pattern})\s*(?:обл\.|область|край|республика|респ\.)',
            # В формате "Москва, улица..."
            rf'\b({cities_pattern})\s*,',
            # Город в скобках или кавычках
            rf'["\(]({cities_pattern})[")\]]'
        ]

        # Компилируем паттерны для лучшей производительности
        self.compiled_city_patterns = [
            re.compile(pattern, re.IGNORECASE | re.UNICODE)
            for pattern in self.city_patterns
        ]

    def _prepare_address_patterns(self):
        """Подготавливает регулярные выражения для поиска адресов"""
        self.address_patterns = [
            # Улицы
            r'(?:ул\.|улица)\s+[А-Яа-яёЁ\s\d\-\.]+(?:,?\s*д\.?\s*\d+[а-я]?)?(?:,?\s*кв\.?\s*\d+)?',
            r'(?:пр\.|проспект)\s+[А-Яа-яёЁ\s\d\-\.]+(?:,?\s*д\.?\s*\d+[а-я]?)?(?:,?\s*кв\.?\s*\d+)?',
            r'(?:пер\.|переулок)\s+[А-Яа-яёЁ\s\d\-\.]+(?:,?\s*д\.?\s*\d+[а-я]?)?(?:,?\s*кв\.?\s*\d+)?',
            r'(?:пл\.|площадь)\s+[А-Яа-яёЁ\s\d\-\.]+(?:,?\s*д\.?\s*\d+[а-я]?)?',
            r'(?:б-р|бульвар)\s+[А-Яа-яёЁ\s\d\-\.]+(?:,?\s*д\.?\s*\d+[а-я]?)?(?:,?\s*кв\.?\s*\d+)?',
            r'(?:наб\.|набережная)\s+[А-Яа-яёЁ\s\d\-\.]+(?:,?\s*д\.?\s*\d+[а-я]?)?(?:,?\s*кв\.?\s*\d+)?',
            r'(?:ш\.|шоссе)\s+[А-Яа-яёЁ\s\d\-\.]+(?:,?\s*д\.?\s*\d+[а-я]?)?(?:,?\s*кв\.?\s*\д+)?',
            r'(?:тер\.|территория)\s+[А-Яа-яёЁ\s\d\-\.]+(?:,?\s*д\.?\s*\d+[а-я]?)?',
            r'(?:мкр\.|микрорайон)\s+[А-Яа-яёЁ\s\d\-\.]+(?:,?\s*д\.?\s*\d+[а-я]?)?(?:,?\s*кв\.?\s*\d+)?',

            # Дома без указания улицы (но с номером)
            r'\bд\.?\s*\d+[а-я]?(?:\s*корп\.?\s*\d+)?(?:\s*стр\.?\s*\d+)?(?:,?\s*кв\.?\s*\d+)?',

            # Адреса в формате "ул. Название, д. 123"
            r'[А-Яа-яёЁ\s]+(?:ул\.|улица|пр\.|проспект|пер\.|переулок|пл\.|площадь|б-р|бульвар|наб\.|набережная|ш\.|шоссе)[А-Яа-яёЁ\s\d\-\.,]+',

            # Почтовые индексы с адресами
            r'\b\d{6}\b[,\s]+[А-Яа-яёЁ\s\d\-\.,]+(?:ул\.|улица|пр\.|проспект|пер\.|переулок|пл\.|площадь|б-р|бульвар|наб\.|набережная|ш\.|шоссе)[А-Яа-яёЁ\s\d\-\.,]+'
        ]

        # Компилируем паттерны для адресов
        self.compiled_address_patterns = [
            re.compile(pattern, re.IGNORECASE | re.UNICODE)
            for pattern in self.address_patterns
        ]

    def extract_locations_and_addresses(self, text):
        """Извлекает города и адреса из текста"""
        if not text or not text.strip():
            return [], []

        try:
            # Очищаем текст от HTML тегов и лишних символов
            clean_text = self._clean_text(text)

            if not clean_text or len(clean_text) < 3:
                return [], []

            # Извлекаем города
            cities = self._extract_cities(clean_text)

            # Извлекаем адреса
            addresses = self._extract_addresses(clean_text)

            return cities, addresses

        except Exception as e:
            self.logger.log(f"Ошибка при анализе текста: {str(e)}", False)
            return [], []

    def _clean_text(self, text):
        """Очищает текст от HTML тегов и лишних символов"""
        # Удаляем HTML теги
        clean_text = re.sub(r'<[^>]+>', ' ', text)

        # Удаляем URL
        clean_text = re.sub(r'http[s]?://\S+', ' ', clean_text)
        clean_text = re.sub(r'www\.\S+', ' ', clean_text)

        # Удаляем email
        clean_text = re.sub(r'\S+@\S+\.\S+', ' ', clean_text)

        # Удаляем телефоны
        clean_text = re.sub(r'[\+]?[0-9\(\)\-\s]{10,}', ' ', clean_text)

        # Нормализуем пробелы
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return clean_text

    def _extract_cities(self, text):
        """Извлекает города из текста"""
        found_cities = set()

        # Применяем все паттерны для поиска городов
        for pattern in self.compiled_city_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                # Получаем найденный город из любой группы захвата
                for group in match.groups():
                    if group:
                        city = group.strip()
                        # Нормализуем название города
                        normalized_city = normalize_city_name(city)
                        if normalized_city:
                            found_cities.add(normalized_city)

        # Дополнительный поиск по точным совпадениям (для коротких названий)
        words = re.findall(r'\b[А-Яа-яёЁ\-]+\b', text)
        for word in words:
            normalized_city = normalize_city_name(word)
            if normalized_city and len(word) >= 3:  # Минимум 3 символа для города
                found_cities.add(normalized_city)

        return list(found_cities)

    def _extract_addresses(self, text):
        """Извлекает адреса из текста"""
        found_addresses = set()

        # Применяем все паттерны для поиска адресов
        for pattern in self.compiled_address_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                address = match.group().strip()
                # Очищаем адрес от лишних символов
                address = self._clean_address(address)
                if address and len(address) > 5:
                    found_addresses.add(address)

        return list(found_addresses)

    def _clean_address(self, address):
        """Очищает адрес от лишних символов"""
        # Удаляем лишние пробелы и знаки препинания в начале и конце
        address = re.sub(r'^[,\.\s]+|[,\.\s]+$', '', address)

        # Нормализуем пробелы
        address = re.sub(r'\s+', ' ', address)

        # Удаляем адреса, которые слишком короткие или содержат только цифры
        if len(address) < 5 or address.isdigit():
            return None

        return address

    def analyze_text_detailed(self, text):
        """Подробный анализ текста с дополнительной информацией"""
        if not text or not text.strip():
            return {
                'cities': [],
                'addresses': [],
                'analysis_info': {
                    'text_length': 0,
                    'cleaned_text_length': 0,
                    'patterns_used': 0
                }
            }

        clean_text = self._clean_text(text)
        cities, addresses = self.extract_locations_and_addresses(text)

        return {
            'cities': cities,
            'addresses': addresses,
            'analysis_info': {
                'text_length': len(text),
                'cleaned_text_length': len(clean_text),
                'cities_found': len(cities),
                'addresses_found': len(addresses),
                'patterns_used': len(self.compiled_city_patterns) + len(self.compiled_address_patterns)
            }
        }

    def get_statistics(self):
        """Возвращает статистику анализатора"""
        return {
            'total_cities_in_database': len(self.cities_list),
            'total_aliases': len(self.city_aliases),
            'city_patterns_count': len(self.compiled_city_patterns),
            'address_patterns_count': len(self.compiled_address_patterns)
        }

