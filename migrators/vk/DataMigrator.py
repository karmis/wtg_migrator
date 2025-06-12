#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json


class DataMigrator:
    """Мигратор данных из VK в целевую базу"""

    def __init__(self, config, logger, text_analyzer):
        self.config = config
        self.logger = logger
        self.text_analyzer = text_analyzer

    def migrate_groups_to_orgs(self, vk_cursor, target_cursor, source_file):
        """Мигрирует данные из vk_groups в orgs с анализом городов"""
        try:
            # Получаем все группы из VK базы
            vk_cursor.execute("SELECT url, descr, last_checked_date, last_post_date, last_event_date FROM vk_groups")
            vk_groups = vk_cursor.fetchall()

            self.logger.log(f"Найдено {len(vk_groups)} групп в {source_file}")

            migrated_count = 0
            skipped_count = 0

            for group in vk_groups:
                url, descr, last_checked_date, last_post_date, last_event_date = group

                # Проверяем, есть ли уже такая организация в основной базе
                target_cursor.execute("SELECT id FROM orgs WHERE url = ?", (url,))
                existing_org = target_cursor.fetchone()

                if not existing_org:
                    # Анализируем города из описания и URL
                    text_data = []
                    if url:
                        text_data.append(url)
                    if descr:
                        text_data.append(descr)

                    combined_text = " ".join(text_data)
                    cities, _ = self.text_analyzer.extract_locations_and_addresses(combined_text)
                    cities_json = json.dumps(cities, ensure_ascii=False) if cities else "[]"

                    # Добавляем новую организацию с городами
                    target_cursor.execute("""
                        INSERT INTO orgs (url, descr_raw, last_checked_date, last_post_date, last_event_date, cities)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (url, descr, last_checked_date, last_post_date, last_event_date, cities_json))
                    migrated_count += 1

                    if cities and migrated_count <= self.config.log_limit_examples:
                        self.logger.log(f"  + Добавлена организация: {url} (города: {cities})", False)
                    elif migrated_count <= self.config.log_limit_examples:
                        self.logger.log(f"  + Добавлена организация: {url}", False)
                else:
                    skipped_count += 1
                    if skipped_count <= self.config.log_limit_examples:
                        self.logger.log(f"  - Пропущена (уже существует): {url}", False)

            self.logger.log(f"Организации из {source_file}: добавлено {migrated_count}, пропущено {skipped_count}")
            return migrated_count

        except Exception as e:
            self.logger.log(f"Ошибка при миграции групп из {source_file}: {str(e)}")
            return 0

    def migrate_posts(self, vk_cursor, target_cursor, source_file, event_detector):
        """Мигрирует данные из vk_posts в posts с анализом городов и адресов"""
        try:
            # Получаем все посты из VK базы с информацией о группах
            vk_cursor.execute("""
                SELECT vp.group_id, vp.post_content, vp.post_date, vp.post_likes, 
                       vp.post_comments, vp.post_reposts, vp.post_images, 
                       vp.vk_group_url, vp.post_id, vg.url
                FROM vk_posts vp
                LEFT JOIN vk_groups vg ON vp.group_id = vg.id
            """)
            vk_posts = vk_cursor.fetchall()

            self.logger.log(f"Найдено {len(vk_posts)} постов в {source_file}")

            migrated_count = 0
            skipped_count = 0
            orphaned_count = 0
            posts_with_cities = 0
            posts_with_addresses = 0

            for post in vk_posts:
                (group_id, post_content, post_date, post_likes, post_comments, post_reposts, post_images, vk_group_url,
                 post_id, group_url) = post

                # Проверяем, есть ли уже такой пост в основной базе
                check_url = group_url or vk_group_url
                if post_id is None or check_url is None:
                    continue
                target_cursor.execute("""
                    SELECT p.id FROM posts p 
                    JOIN orgs o ON p.org_id = o.id 
                    WHERE p.post_id = ? AND o.url = ?
                """, (post_id, check_url))
                existing_post = target_cursor.fetchone()

                if not existing_post:
                    # Находим org_id по URL группы
                    target_cursor.execute("SELECT id FROM orgs WHERE url = ?", (group_url or vk_group_url,))
                    org_result = target_cursor.fetchone()

                    if org_result:
                        org_id = org_result[0]

                        # Анализируем города и адреса из контента поста
                        cities, addresses = self.text_analyzer.extract_locations_and_addresses(post_content)
                        cities_json = json.dumps(cities, ensure_ascii=False) if cities else "[]"
                        addresses_json = json.dumps(addresses, ensure_ascii=False) if addresses else "[]"
                        is_event = event_detector.is_event_invitation(post_content)
                        # Добавляем новый пост с городами и адресами
                        target_cursor.execute("""
                            INSERT INTO posts (org_id, post_content, content, post_date, 
                                             post_likes, post_comments, post_reposts, 
                                             post_images, images, post_id, cities, address, maybe_event)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (org_id, post_content, post_content, post_date, post_likes, post_comments, post_reposts,
                              post_images, post_images, post_id, cities_json, addresses_json, is_event))

                        migrated_count += 1

                        if cities:
                            posts_with_cities += 1
                        if addresses:
                            posts_with_addresses += 1

                        if migrated_count <= self.config.log_limit_examples:
                            city_info = f" (города: {cities})" if cities else ""
                            addr_info = f" (адреса: {addresses})" if addresses else ""
                            self.logger.log(
                                f"  + Добавлен пост {post_id} для {group_url or vk_group_url}{city_info}{addr_info}",
                                False)
                    else:
                        orphaned_count += 1
                        content_preview = (post_content[:100] + "...") if post_content and len(
                            post_content) > 100 else (post_content or "Нет контента")

                        if orphaned_count <= self.config.log_limit_examples:
                            self.logger.log(
                                f"  ! Пост {post_id} пропущен - не найдена организация для {group_url or vk_group_url}",
                                False)
                            self.logger.log(f"    Group ID: {group_id}, Дата: {post_date}", False)
                            self.logger.log(
                                f"    Лайки: {post_likes}, Комментарии: {post_comments}, Репосты: {post_reposts}",
                                False)
                            self.logger.log(f"    Контент: {content_preview}", False)
                else:
                    skipped_count += 1
                    content_preview = (post_content[:50] + "...") if post_content and len(post_content) > 50 else (
                            post_content or "Нет контента")

                    if skipped_count <= self.config.log_limit_examples:
                        self.logger.log(f"  - Пропущен пост {post_id} (уже существует)", False)
                        self.logger.log(f"    Организация: {group_url or vk_group_url}, Дата: {post_date}", False)
                        self.logger.log(
                            f"    Лайки: {post_likes}, Комментарии: {post_comments}, Репосты: {post_reposts}", False)
                        self.logger.log(f"    Контент: {content_preview}", False)

            self.logger.log(
                f"Посты из {source_file}: добавлено {migrated_count}, пропущено {skipped_count}, без организации {orphaned_count}")
            self.logger.log(f"  - с найденными городами: {posts_with_cities}")
            self.logger.log(f"  - с найденными адресами: {posts_with_addresses}")
            return migrated_count

        except Exception as e:
            self.logger.log(f"Ошибка при миграции постов из {source_file}: {str(e)}")
            return 0
