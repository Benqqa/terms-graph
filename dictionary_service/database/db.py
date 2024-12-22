"""Модуль для работы с базой данных"""

import logging
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from dictionary_service.exceptions.errors import DatabaseError, TermNotFoundError, TermExistsError
from dictionary_service.models.term import Term
from dictionary_service.initial_data import INITIAL_TERMS

logger = logging.getLogger(__name__)

class DictionaryDB:
    """Класс для работы с базой данных словаря"""
    
    def __init__(self, db_path: str = 'dictionary.db'):
        """
        Инициализация базы данных
        
        Args:
            db_path: Путь к файлу базы данных
        """
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.create_tables()
            self.initialize_data()
        except sqlite3.Error as e:
            logger.error(f"Ошибка при инициализации БД: {e}")
            raise DatabaseError(f"Не удалось инициализировать базу данных: {e}")
    
    def initialize_data(self) -> None:
        """Инициализация начальных данных из initial_data.py"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM terms')
            if cursor.fetchone()[0] == 0:
                logger.info("Инициализация начальных данных")
                for term_data in INITIAL_TERMS:
                    term = Term(
                        name=term_data['name'],
                        definition=term_data['definition'],
                        source=term_data['source'],
                        related_terms=term_data['related_terms'],
                        relations=term_data['relations']
                    )
                    self.add_term(term)
                logger.info("Начальные данные успешно добавлены")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при инициализации данных: {e}")
            raise DatabaseError(f"Не удалось инициализировать данные: {e}")
    
    def create_tables(self) -> None:
        """Создание таблиц в базе данных"""
        try:
            cursor = self.conn.cursor()
            # Таблица терминов
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                definition TEXT NOT NULL,
                source TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            ''')
            
            # Таблица связей между терминами
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS related_terms (
                term_id INTEGER,
                related_term TEXT,
                relation_type TEXT,
                FOREIGN KEY(term_id) REFERENCES terms(id) ON DELETE CASCADE,
                PRIMARY KEY(term_id, related_term)
            )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            raise DatabaseError(f"Не удалось создать таблицы: {e}")

    def add_term(self, term: Term) -> Tuple[bool, str, Optional[int]]:
        """
        Добавление нового термина
        
        Args:
            term: Объект термина для добавления
        Returns:
            Tuple[bool, str, Optional[int]]: (успех, сообщение, id термина)
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                '''INSERT INTO terms 
                   (name, definition, source, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?)''',
                (term.name.lower(), term.definition, term.source, 
                 term.created_at, term.updated_at)
            )
            term_id = cursor.lastrowid
            
            # Добавляем связанные термины
            for related_term in term.related_terms:
                cursor.execute(
                    '''INSERT INTO related_terms 
                       (term_id, related_term, relation_type) 
                       VALUES (?, ?, ?)''',
                    (term_id, related_term, 
                     term.relations.get(related_term, 'связан с'))
                )
            
            self.conn.commit()
            logger.info(f"Добавлен новый термин: {term.name}")
            return True, "Термин успешно добавлен", term_id
        except sqlite3.IntegrityError:
            logger.warning(f"Попытка добавить существующий термин: {term.name}")
            return False, "Термин уже существует", None
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении термина {term.name}: {e}")
            return False, f"Ошибка при добавлении термина: {e}", None

    def get_term(self, term_id: Optional[int] = None, name: Optional[str] = None) -> Term:
        """
        Получение термина по ID или имени
        
        Args:
            term_id: ID термина
            name: Имя термина
        Returns:
            Term: Объект термина
        Raises:
            TermNotFoundError: Если термин не найден
        """
        try:
            cursor = self.conn.cursor()
            if term_id:
                cursor.execute('SELECT * FROM terms WHERE id = ?', (term_id,))
            else:
                cursor.execute('SELECT * FROM terms WHERE LOWER(name) = LOWER(?)', (name,))
            
            row = cursor.fetchone()
            if not row:
                raise TermNotFoundError(f"Термин не найден: {name or term_id}")
                
            # Получаем связанные термины
            cursor.execute('''SELECT related_term, relation_type 
                            FROM related_terms WHERE term_id = ?''', (row['id'],))
            related_data = cursor.fetchall()
            
            return Term.from_db_row(row, related_data)
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении термина: {e}")
            raise DatabaseError(f"Не удалось получить термин: {e}")

    def list_terms(self) -> List[Term]:
        """
        Получение списка всех терминов
        
        Returns:
            List[Term]: Список всех терминов
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM terms')
            terms = []
            for row in cursor.fetchall():
                # Получаем связанные термины для каждого термина
                cursor.execute('''SELECT related_term, relation_type 
                                FROM related_terms WHERE term_id = ?''', (row['id'],))
                related_data = cursor.fetchall()
                terms.append(Term.from_db_row(row, related_data))
            return terms
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении списка терминов: {e}")
            raise DatabaseError(f"Не удалось получить список терминов: {e}")

    def update_term(self, term_id: int, term: Term) -> Tuple[bool, str]:
        """
        Обновление существующего термина
        
        Args:
            term_id: ID термина для обновления
            term: Новые данные термина
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.utcnow().isoformat()
            
            # Проверяем существование термина
            cursor.execute('SELECT id FROM terms WHERE id = ?', (term_id,))
            if not cursor.fetchone():
                logger.warning(f"Попытка обновить несуществующий термин: {term_id}")
                return False, "Термин не найден"
            
            # Обновляем основные данные термина
            cursor.execute(
                'UPDATE terms SET name=?, definition=?, source=?, updated_at=? WHERE id=?',
                (term.name.lower(), term.definition, term.source, now, term_id)
            )
            
            # Обновляем связанные термины
            cursor.execute('DELETE FROM related_terms WHERE term_id=?', (term_id,))
            for related_term in term.related_terms:
                cursor.execute(
                    '''INSERT INTO related_terms 
                       (term_id, related_term, relation_type) 
                       VALUES (?, ?, ?)''',
                    (term_id, related_term, 
                     term.relations.get(related_term, 'связан с'))
                )
            
            self.conn.commit()
            logger.info(f"Обновлен термин: {term.name}")
            return True, "Термин успешно обновлен"
        except sqlite3.Error as e:
            logger.error(f"Ошибка при обновлении термина {term_id}: {e}")
            return False, f"Ошибка при обновлении термина: {e}"

    def delete_term(self, term_id: int) -> Tuple[bool, str]:
        """
        Удаление термина
        
        Args:
            term_id: ID термина для удаления
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        try:
            cursor = self.conn.cursor()
            
            # Проверяем существование термина
            cursor.execute('SELECT id FROM terms WHERE id = ?', (term_id,))
            if not cursor.fetchone():
                logger.warning(f"Попытка удалить несуществующий термин: {term_id}")
                return False, "Термин не найден"
            
            cursor.execute('DELETE FROM related_terms WHERE term_id=?', (term_id,))
            cursor.execute('DELETE FROM terms WHERE id=?', (term_id,))
            self.conn.commit()
            
            logger.info(f"Удален термин с ID: {term_id}")
            return True, "Термин успешно удален"
        except sqlite3.Error as e:
            logger.error(f"Ошибка при удалении термина {term_id}: {e}")
            return False, f"Ошибка при удалении термина: {e}" 