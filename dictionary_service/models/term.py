"""Модуль с моделью термина"""

from typing import Dict, List, Optional
from datetime import datetime
import dictionary_pb2

class Term:
    """Модель термина"""
    
    def __init__(self, 
                 name: str,
                 definition: str,
                 source: Optional[str] = None,
                 related_terms: Optional[List[str]] = None,
                 relations: Optional[Dict[str, str]] = None,
                 term_id: Optional[int] = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None):
        """
        Инициализация термина
        
        Args:
            name: Название термина
            definition: Определение термина
            source: Источник термина
            related_terms: Список связанных терминов
            relations: Словарь связей термина
            term_id: ID термина
            created_at: Дата создания
            updated_at: Дата обновления
        """
        self.id = term_id
        self.name = name
        self.definition = definition
        self.source = source or ""
        self.related_terms = related_terms or []
        self.relations = relations or {}
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or self.created_at

    @classmethod
    def from_db_row(cls, row: Dict, related_data: List[Dict]) -> 'Term':
        """
        Создание термина из данных БД
        
        Args:
            row: Строка из таблицы terms
            related_data: Данные о связанных терминах
        Returns:
            Term: Объект термина
        """
        return cls(
            term_id=row['id'],
            name=row['name'],
            definition=row['definition'],
            source=row['source'],
            related_terms=[r['related_term'] for r in related_data],
            relations={r['related_term']: r['relation_type'] for r in related_data},
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    @classmethod
    def from_proto(cls, proto: dictionary_pb2.Term) -> 'Term':
        """
        Создание термина из protobuf объекта
        
        Args:
            proto: Protobuf объект термина
        Returns:
            Term: Объект термина
        """
        return cls(
            name=proto.name,
            definition=proto.definition,
            source=proto.source,
            related_terms=list(proto.related_terms),
            relations=dict(proto.relations)
        )

    def to_proto(self) -> dictionary_pb2.Term:
        """
        Преобразование в protobuf объект
        
        Returns:
            dictionary_pb2.Term: Protobuf объект термина
        """
        proto = dictionary_pb2.Term(
            id=self.id,
            name=self.name,
            definition=self.definition,
            source=self.source,
            related_terms=self.related_terms,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
        for related, relation in self.relations.items():
            proto.relations[related] = relation
        return proto

    def to_dict(self) -> Dict:
        """
        Преобразование в словарь
        
        Returns:
            Dict: Словарь с данными термина
        """
        return {
            'id': self.id,
            'name': self.name,
            'definition': self.definition,
            'source': self.source,
            'related_terms': self.related_terms,
            'relations': self.relations,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 