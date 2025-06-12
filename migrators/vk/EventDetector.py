# Ключевые слова, характерные для приглашений на мероприятия
import re
from typing import Dict, Tuple, List


class EventDetector:
    """Класс для определения постов-приглашений на мероприятия"""

    # Ключевые слова, характерные для приглашений на мероприятия
    INVITATION_KEYWORDS = ['приглашаем', 'приглашение', 'ждем вас', 'ждём вас', 'добро пожаловать', 'скоро состоится',
        'состоится', 'проводится', 'пройдет', 'пройдёт', 'встреча', 'мероприятие', 'событие', 'конференция', 'семинар',
        'вебинар', 'тренинг', 'мастер-класс', 'воркшоп', 'презентация', 'выставка', 'фестиваль', 'концерт', 'спектакль',
        'показ', 'регистрация', 'записаться', 'участие', 'участвовать', 'не пропустите', 'успейте',
        'ограниченное количество мест', 'бесплатный вход', 'билеты', 'вход свободный', 'запись открыта', 'приходите',
        'ждем', 'ждём', 'встречаемся', 'увидимся', 'открываем', 'открытие', 'откроется', 'бронь', 'бронируйте',
        'забронировать', # Добавляем новые ключевые слова для ресторанных/развлекательных событий
        'бронирование', 'бронирование стола', 'забронировать стол', 'столы', 'уикенд', 'выходные', 'классные события',
        'события', 'впереди', 'можно принести', 'со своим', 'алкоголь', 'администратор', 'подробности', 'телефон',
        'звоните', 'связаться', # Новые ключевые слова из примера
        'планы на вечер', 'планы', 'открываемся', 'новое меню', 'меню', 'специальная', 'винная карта', 'вино', 'бокал',
        'бутылка', 'танцы', 'live-концерт', 'концерт', 'live', 'main stage', 'stage', 'veranda', 'веранда',
        'летняя веранда', 'свободный вход', 'вход свободный', 'по спискам', 'списки', 'список', 'действует', 'при брони',
        'брони стола', 'всю ночь', 'после полуночи', 'без списков', 'девушкам', 'присылайте', 'фамилии', 'директ', 'dj',
        'диджей', 'сет', 'выступление', 'программа']

    # Слова, указывающие на место проведения
    LOCATION_KEYWORDS = ['адрес', 'место', 'проводится', 'состоится', 'пройдет', 'пройдёт', 'ул.', 'улица', 'проспект',
        'пр.', 'площадь', 'пл.', 'переулок', 'пер.', 'офис', 'здание', 'центр', 'зал', 'аудитория', 'кабинет', 'комната',
        'онлайн', 'zoom', 'teams', 'skype', 'discord', 'meet', 'телеграм', 'где:', 'адрес:', 'место:', 'локация',
        # Новые локации из примера
        'веранда', 'летняя веранда', 'main stage', 'veranda', 'сцена', 'танцпол', 'бар', 'ресторан', 'клуб', 'заведение']

    # Паттерны для определения времени
    TIME_PATTERNS = [r'\b(\d{1,2}):(\d{2})\b',  # 14:30
        r'\b(\d{1,2})\.(\d{2})\b',  # 14.30
        r'\b(\d{1,2})\s*ч\s*(\d{2})\s*мин\b',  # 14 ч 30 мин
        r'\b(\d{1,2})\s*часов?\b',  # 14 часов
        r'\bв\s+(\d{1,2}):(\d{2})\b',  # в 14:30
        r'\bс\s+(\d{1,2}):(\d{2})\b',  # с 14:30
        r'\bначало\s+в?\s*(\d{1,2}):(\d{2})\b',  # начало в 14:30
        r'\bвремя:\s*(\d{1,2}):(\d{2})\b',  # время: 14:30
        r'\bво\s+сколько:\s*(\d{1,2}):(\d{2})\b',  # во сколько: 14:30
        # Добавляем паттерны для временных диапазонов
        r'\bс\s+(\d{1,2}):(\d{2})\s+и?\s*до\s+(\d{1,2}):(\d{2})\b',  # с 18:00 и до 22:00
        r'\bс\s+(\d{1,2}):(\d{2})\s+до\s+(\d{1,2}):(\d{2})\b',  # с 18:00 до 22:00
        r'\b(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\b',  # 18:00-22:00
        # Новые паттерны времени из примера
        r'\b(\d{1,2}):(\d{2})\s+[A-Za-zА-Яа-я]',  # 23:00 Live-концерт
        r'\bдо\s+(\d{1,2}):(\d{2})\b',  # до 01:00
        r'\bпосле\s+полуночи\b',  # после полуночи
        r'\bвсю\s+ночь\b',  # всю ночь
        r'\bна\s+вечер\b',  # на вечер
        r'\bвечер[а-я]*\b',  # вечер, вечера, вечером
    ]

    # Паттерны для определения даты
    DATE_PATTERNS = [r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b',  # 25.12.2024
        r'\b(\d{1,2})\/(\d{1,2})\/(\d{4})\b',  # 25/12/2024
        r'\b(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})\b',
        r'\b(\d{1,2})\s+(янв|фев|мар|апр|май|июн|июл|авг|сен|окт|ноя|дек)\.?\s+(\d{4})\b',
        r'\b(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря),?\s+(понедельник|вторник|среда|четверг|пятница|суббота|воскресенье)\b',
        # 6 июня, пятница
        r'\b(\d{1,2})\s+(янв|фев|мар|апр|май|июн|июл|авг|сен|окт|ноя|дек)\.?,?\s+(понедельник|вторник|среда|четверг|пятница|суббота|воскресенье)\b',
        # 6 июн, пятница
        r'\b(понедельник|вторник|среда|четверг|пятница|суббота|воскресенье),?\s+(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\b',
        # пятница, 6 июня
        r'\b(понедельник|вторник|среда|четверг|пятница|суббота|воскресенье),?\s+(\d{1,2})\s+(янв|фев|мар|апр|май|июн|июл|авг|сен|окт|ноя|дек)\.?\b',
        # пятница, 6 июн
        r'\b(понедельник|вторник|среда|четверг|пятница|суббота|воскресенье)\b', r'\b(завтра|послезавтра|сегодня)\b',
        r'\b(\d{1,2})\s+числа\b', r'\bдата:\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\b',  # дата: 25.12.2024
        r'\bкогда:\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\b',  # когда: 25.12.2024
        r'\b(\d{1,2})-го\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\b',
        r'\b(\d{1,2})-го\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря),?\s+(понедельник|вторник|среда|четверг|пятница|суббота|воскресенье)\b',
        # 6-го июня, пятница
        # Добавляем паттерны для временных периодов
        r'\b(большой\s+)?уикенд\b',  # большой уикенд, уикенд
        r'\b(выходные|выходных)\b',  # выходные
        r'\b(впереди)\b',  # впереди (указывает на будущие события)
        # Новые паттерны из примера
        r'\bна\s+вечер\b',  # на вечер
        r'\bвечер[а-я]*\b',  # вечер, вечера, вечером
        r'\bсегодня\s+вечером\b',  # сегодня вечером
        r'\bэтим\s+вечером\b',  # этим вечером
    ]

    # Паттерны для контактной информации
    CONTACT_PATTERNS = [r'\b(\d{2})-(\d{2})-(\d{2})\b',  # 77-95-76
        r'\b(\d{3})-(\d{2})-(\d{2})\b',  # 777-95-76
        r'\b(\d{1,3})-(\d{2,3})-(\d{2,3})\b',  # различные форматы телефонов
        r'\b\+?[78][\s\-]?\(?(\d{3})\)?[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})\b',  # +7(xxx)xxx-xx-xx
        r'\bтелефон[у:]?\s*(\d+[\-\s\d]+)\b',  # телефон: номер
        r'\bзвоните\s+по\s+(\d+[\-\s\d]+)\b',  # звоните по номеру
        r'\bприсылайте\b',  # присылайте (контактное действие)
        r'\bв\s+директ\b',  # в директ
        r'\bфамилии\b',  # фамилии (для списков)
    ]

    # Паттерны для цен и стоимости (часто указываются в событиях)
    PRICE_PATTERNS = [r'\b(\d+)\s*₽\b',  # 250₽
        r'\b(\d+)\s*руб\b',  # 250 руб
        r'\bот\s+(\d+)\s*₽\b',  # от 250₽
        r'\bза\s+(\d+)\s*₽\b',  # за 250₽
        r'\b(\d+)\s*₽\s+за\s+\w+\b',  # 250₽ за бокал
        r'\bбесплатн[ой]\b',  # бесплатно, бесплатный
        r'\bсвободный\s+вход\b',  # свободный вход
        r'\bвход\s+свободный\b',  # вход свободный
    ]

    # Паттерны для программы мероприятий
    PROGRAM_PATTERNS = [r'\b(\d{1,2}):(\d{2})\s+[A-Za-zА-Яа-я]',  # 23:00 Live-концерт
        r'\bmain\s+stage\b',  # main stage
        r'\bveranda\b',  # veranda
        r'\blive[-\s]концерт\b',  # live-концерт
        r'\b[A-Z][a-z]+\s*/\s*[A-Z][a-z]+\b',  # Lacoste / Raimov
        r'\b[A-Z][a-z]+\s*/\s*[A-Z][a-z]+\s*/\s*[A-Z][a-z]+\b',  # тройные имена
    ]

    def __init__(self, logger=None):
        """Инициализация детектора событий"""
        self.logger = logger

    def is_event_invitation(self, content: str) -> bool:
        """
        Определяет, является ли пост приглашением на мероприятие

        Args:
            content: Текст поста для анализа

        Returns:
            bool: True если пост

        """
        if not content:
            return False

        content_lower = content.lower()

        # Проверяем наличие ключевых слов приглашения
        has_invitation_keywords = self._has_invitation_keywords(content_lower)

        # Проверяем наличие даты
        has_date = self._has_date_mention(content_lower)

        # Проверяем наличие времени
        has_time = self._has_time_mention(content_lower)

        # Проверяем наличие места
        has_location = self._has_location_mention(content_lower)

        # Проверяем наличие контактной информации
        has_contact = self._has_contact_mention(content_lower)

        # Проверяем наличие цен
        has_prices = self._has_price_mention(content)

        # Проверяем наличие программы мероприятия
        has_program = self._has_program_mention(content)

        # Расширенная логика определения события:
        # 1. Классический вариант: ключевые слова + (дата ИЛИ время ИЛИ место)
        # 2. Развлекательный вариант: время + контакты + (цены ИЛИ программа)
        # 3. Программный вариант: программа + время + (контакты ИЛИ цены)
        # 4. Ресторанный вариант: ключевые слова + время + цены

        is_event = (
            # Классический вариант
            (has_invitation_keywords and (has_date or has_time or has_location)) or
            # Развлекательный вариант
            (has_time and has_contact and (has_prices or has_program)) or
            # Программный вариант
            (has_program and has_time and (has_contact or has_prices)) or
            # Ресторанный вариант
            (has_invitation_keywords and has_time and has_prices) or
            # Комплексный вариант (много индикаторов)
            (sum([has_invitation_keywords, has_time, has_contact, has_prices, has_program]) >= 3)
        )

        if self.logger and is_event:
            self.logger.log(f"    Обнаружено приглашение на мероприятие", False)

        return is_event

    def _has_price_mention(self, content: str) -> bool:
        """Проверяет наличие упоминания цен"""
        for pattern in self.PRICE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _has_program_mention(self, content: str) -> bool:
        """Проверяет наличие программы мероприятия"""
        for pattern in self.PROGRAM_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _has_contact_mention(self, content: str) -> bool:
        """Проверяет наличие контактной информации"""
        for pattern in self.CONTACT_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _has_service_keywords(self, content: str) -> bool:
        """Проверяет наличие ключевых слов сервиса/услуг"""
        service_keywords = [
            'бронирование', 'бронь', 'стол', 'столы', 'ресторан', 'кафе',
            'администратор', 'подробности', 'услуги', 'сервис', 'меню',
            'винная карта', 'бар', 'клуб', 'заведение'
        ]
        for keyword in service_keywords:
            if keyword in content:
                return True
        return False

    def _has_invitation_keywords(self, content: str) -> bool:
        """Проверяет наличие ключевых слов приглашения"""
        for keyword in self.INVITATION_KEYWORDS:
            if keyword in content:
                return True
        return False

    def _has_date_mention(self, content: str) -> bool:
        """Проверяет наличие упоминания даты"""
        for pattern in self.DATE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _has_time_mention(self, content: str) -> bool:
        """Проверяет наличие упоминания времени"""
        for pattern in self.TIME_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def _has_location_mention(self, content: str) -> bool:
        """Проверяет наличие упоминания места"""
        for keyword in self.LOCATION_KEYWORDS:
            if keyword in content:
                return True
        return False

    def _get_found_keywords(self, content: str) -> List[str]:
        """Возвращает найденные ключевые слова"""
        found = []
        for keyword in self.INVITATION_KEYWORDS:
            if keyword in content:
                found.append(keyword)
        return found

    def get_event_analysis(self, content: str) -> Dict:
        """
        Получает детальную информацию о том, почему пост считается/не считается приглашением

        Args:
            content: Текст поста для анализа

        Returns:
            Dict: Детальный анализ поста
        """
        if not content:
            return {
                'is_event': False,
                'has_invitation_keywords': False,
                'has_date': False,
                'has_time': False,
                'has_location': False,
                'has_contact': False,
                'has_prices': False,
                'has_program': False,
                'has_service_keywords': False,
                'found_keywords': []
            }

        content_lower = content.lower()

        return {
            'is_event': self.is_event_invitation(content),
            'has_invitation_keywords': self._has_invitation_keywords(content_lower),
            'has_date': self._has_date_mention(content_lower),
            'has_time': self._has_time_mention(content_lower),
            'has_location': self._has_location_mention(content_lower),
            'has_contact': self._has_contact_mention(content_lower),
            'has_prices': self._has_price_mention(content),
            'has_program': self._has_program_mention(content),
            'has_service_keywords': self._has_service_keywords(content_lower),
            'found_keywords': self._get_found_keywords(content_lower)
        }

    def analyze_batch(self, posts: List[Tuple]) -> Dict:
        """
        Анализирует пакет постов и возвращает статистику

        Args:
            posts: Список кортежей (post_id, content)

        Returns:
            Dict: Статистика анализа
        """
        total_posts = len(posts)
        event_posts = 0
        analyzed_posts = []

        for post_id, content in posts:
            is_event = self.is_event_invitation(content)
            if is_event:
                event_posts += 1
            analyzed_posts.append((post_id, is_event))

        return {
            'total_posts': total_posts,
            'event_posts': event_posts,
            'regular_posts': total_posts - event_posts,
            'event_percentage': (event_posts / total_posts * 100) if total_posts > 0 else 0,
            'analyzed_posts': analyzed_posts
        }

