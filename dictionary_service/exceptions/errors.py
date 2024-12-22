"""Модуль с определениями исключений"""

class DatabaseError(Exception):
    """Базовый класс для ошибок базы данных"""
    pass

class TermNotFoundError(DatabaseError):
    """Исключение, когда термин не найден"""
    pass

class TermExistsError(DatabaseError):
    """Исключение, когда термин уже существует"""
    pass 