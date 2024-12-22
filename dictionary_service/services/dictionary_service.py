"""Модуль с реализацией gRPC сервиса"""

import logging
import grpc
import dictionary_pb2
import dictionary_pb2_grpc

from dictionary_service.database.db import DictionaryDB
from dictionary_service.models.term import Term
from dictionary_service.exceptions.errors import DatabaseError, TermNotFoundError

logger = logging.getLogger(__name__)

class DictionaryService(dictionary_pb2_grpc.DictionaryServiceServicer):
    """Реализация gRPC сервиса словаря"""
    
    def __init__(self, db_path: str = 'dictionary.db'):
        """
        Инициализация сервиса
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db = DictionaryDB(db_path)
    
    def GetDefinition(self, request: dictionary_pb2.TermRequest, 
                     context: grpc.ServicerContext) -> dictionary_pb2.DefinitionResponse:
        """Получение определения термина"""
        try:
            term = self.db.get_term(name=request.name)
            return dictionary_pb2.DefinitionResponse(term=term.to_proto())
        except TermNotFoundError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return dictionary_pb2.DefinitionResponse()
        except DatabaseError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dictionary_pb2.DefinitionResponse()
    
    def ListTerms(self, request: dictionary_pb2.ListTermsRequest, 
                 context: grpc.ServicerContext) -> dictionary_pb2.ListTermsResponse:
        """Получение списка всех терминов"""
        try:
            terms = self.db.list_terms()
            return dictionary_pb2.ListTermsResponse(
                terms=[term.to_proto() for term in terms]
            )
        except DatabaseError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dictionary_pb2.ListTermsResponse()
    
    def AddTerm(self, request: dictionary_pb2.AddTermRequest, 
                context: grpc.ServicerContext) -> dictionary_pb2.AddTermResponse:
        """Добавление нового термина"""
        try:
            term = Term.from_proto(request.term)
            success, message, term_id = self.db.add_term(term)
            return dictionary_pb2.AddTermResponse(success=success, message=message)
        except DatabaseError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dictionary_pb2.AddTermResponse(success=False, message=str(e))
    
    def UpdateTerm(self, request: dictionary_pb2.UpdateTermRequest, 
                  context: grpc.ServicerContext) -> dictionary_pb2.UpdateTermResponse:
        """Обновление существующего термина"""
        try:
            term = Term.from_proto(request.term)
            success, message = self.db.update_term(request.id, term)
            updated_term = None
            if success:
                updated_term = self.db.get_term(term_id=request.id).to_proto()
            return dictionary_pb2.UpdateTermResponse(
                success=success, 
                message=message, 
                term=updated_term
            )
        except DatabaseError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dictionary_pb2.UpdateTermResponse(success=False, message=str(e))
    
    def DeleteTerm(self, request: dictionary_pb2.DeleteTermRequest, 
                  context: grpc.ServicerContext) -> dictionary_pb2.DeleteTermResponse:
        """Удаление термина"""
        try:
            success, message = self.db.delete_term(request.id)
            return dictionary_pb2.DeleteTermResponse(success=success, message=message)
        except DatabaseError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dictionary_pb2.DeleteTermResponse(success=False, message=str(e)) 