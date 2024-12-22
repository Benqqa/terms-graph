from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, Response
import grpc
import dictionary_pb2
import dictionary_pb2_grpc
import os
from flask_cors import CORS
import logging
from typing import Dict, List, Union
from functools import wraps

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация приложения
class Config:
    """Конфигурация приложения"""
    DICTIONARY_HOST = os.getenv("DICTIONARY_HOST", "localhost")
    DICTIONARY_PORT = int(os.getenv("DICTIONARY_PORT", "50051"))
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", "5000"))

app = Flask(__name__)
CORS(app)

# Создание gRPC канала и клиента
class GrpcClient:
    """Класс для работы с gRPC клиентом"""
    _instance = None
    _channel = None
    _stub = None

    @classmethod
    def get_instance(cls) -> dictionary_pb2_grpc.DictionaryServiceStub:
        """Получение экземпляра gRPC клиента"""
        if cls._instance is None:
            cls._channel = grpc.insecure_channel(
                f"{Config.DICTIONARY_HOST}:{Config.DICTIONARY_PORT}"
            )
            cls._stub = dictionary_pb2_grpc.DictionaryServiceStub(cls._channel)
            cls._instance = cls._stub
        return cls._instance

def handle_grpc_error(f):
    """Декоратор для обработки gRPC ошибок"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except grpc.RpcError as e:
            logger.error(f"gRPC Error in {f.__name__}: {str(e)}")
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return render_template('term_not_found.html', term_name=kwargs.get('name', 'Unknown'))
            return render_template('error.html', 
                error=f"Произошла ошибка при обращении к сервису: {e.details()}")
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return render_template('error.html', 
                error="Произошла неожиданная ошибка")
    return wrapper

@app.route('/static/<path:path>')
def send_static(path: str) -> Response:
    """Отправка статических файлов"""
    return send_from_directory('static', path)

@app.route('/')
@handle_grpc_error
def index() -> str:
    """Главная страница со списком терминов"""
    response = GrpcClient.get_instance().ListTerms(dictionary_pb2.ListTermsRequest())
    return render_template('database.html', terms=response.terms)

@app.route('/term/<name>')
@handle_grpc_error
def get_term(name: str) -> str:
    """
    Страница с определением термина
    
    Args:
        name: Имя термина
    Returns:
        str: HTML страница с определением термина
    """
    # Получаем все термины для поиска правильного регистра
    terms_response = GrpcClient.get_instance().ListTerms(dictionary_pb2.ListTermsRequest())
    term_names = {term.name.lower(): term.name for term in terms_response.terms}
    
    # Ищем точное имя термина по нормализованному ключу
    actual_name = term_names.get(name.lower())
    if not actual_name:
        return render_template('term_not_found.html', term_name=name)
    
    # Используем точное имя термина для поиска
    response = GrpcClient.get_instance().GetDefinition(
        dictionary_pb2.TermRequest(name=actual_name)
    )
    return render_template('term.html', term=response.term)

@app.route('/api/terms', methods=['POST'])
@handle_grpc_error
def add_term() -> tuple[Response, int]:
    """API endpoint для добавления термина"""
    data = request.json
    term = dictionary_pb2.Term(
        name=data['name'],
        definition=data['definition'],
        related_terms=data.get('related_terms', []),
        source=data.get('source', '')
    )
    
    # Добавляем связи между терминами
    for related, relation_type in data.get('relations', {}).items():
        term.relations[related] = relation_type

    response = GrpcClient.get_instance().AddTerm(dictionary_pb2.AddTermRequest(term=term))
    return jsonify({
        'success': response.success,
        'message': response.message
    }), 200 if response.success else 400

@app.route('/api/terms/<int:term_id>', methods=['PUT'])
@handle_grpc_error
def update_term(term_id: int) -> tuple[Response, int]:
    """
    API endpoint для обновления термина
    
    Args:
        term_id: ID термина для обновления
    Returns:
        tuple[Response, int]: JSON ответ и HTTP статус
    """
    data = request.json
    term = dictionary_pb2.Term(
        name=data['name'],
        definition=data['definition'],
        related_terms=data.get('related_terms', []),
        source=data.get('source', '')
    )
    
    # Добавляем связи между терминами
    for related, relation_type in data.get('relations', {}).items():
        term.relations[related] = relation_type

    response = GrpcClient.get_instance().UpdateTerm(
        dictionary_pb2.UpdateTermRequest(id=term_id, term=term)
    )
    
    return jsonify({
        'success': response.success,
        'message': response.message,
        'term': {
            'id': response.term.id,
            'name': response.term.name,
            'definition': response.term.definition,
            'source': response.term.source,
            'related_terms': list(response.term.related_terms)
        } if response.term else None
    }), 200 if response.success else 400

@app.route('/api/terms/<int:term_id>', methods=['DELETE'])
@handle_grpc_error
def delete_term(term_id: int) -> tuple[Response, int]:
    """
    API endpoint для удаления термина
    
    Args:
        term_id: ID термина для удаления
    Returns:
        tuple[Response, int]: JSON ответ и HTTP статус
    """
    response = GrpcClient.get_instance().DeleteTerm(
        dictionary_pb2.DeleteTermRequest(id=term_id)
    )
    return jsonify({
        'success': response.success,
        'message': response.message
    }), 200 if response.success else 400

@app.route('/mindmap')
@handle_grpc_error
def mindmap() -> str:
    """
    Страница с визуализацией связей между терминами
    
    Returns:
        str: HTML страница с визуализацией
    """
    response = GrpcClient.get_instance().ListTerms(dictionary_pb2.ListTermsRequest())
    term_names = {term.name.lower(): term.name for term in response.terms}
    
    terms_data = [{
        'id': term.id,
        'name': term.name,
        'definition': term.definition,
        'related_terms': [
            name.split('(')[0].strip()
            for name in term.related_terms
        ],
        'source': term.source,
        'created_at': term.created_at,
        'updated_at': term.updated_at,
        'relations': {
            k.split('(')[0].strip(): v
            for k, v in term.relations.items()
        }
    } for term in response.terms]

    # Проверяем существование связанных терминов
    for term_data in terms_data:
        for related in term_data['related_terms']:
            if related.lower() not in term_names:
                logger.warning(
                    f"Term '{term_data['name']}' references non-existent term '{related}'"
                )

    logger.debug(f"Terms data: {terms_data}")
    return render_template('mindmap.html', terms=terms_data)

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 