"""Модуль для запуска gRPC сервера"""

import logging
from concurrent import futures
import grpc
import dictionary_pb2_grpc
from dictionary_service.services.dictionary_service import DictionaryService

logger = logging.getLogger(__name__)

def serve(host: str = "[::]:50051", max_workers: int = 10) -> None:
    """
    Запуск gRPC сервера
    
    Args:
        host: Адрес и порт для прослушивания
        max_workers: Максимальное количество рабочих потоков
    """
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        dictionary_pb2_grpc.add_DictionaryServiceServicer_to_server(
            DictionaryService(), server
        )
        server.add_insecure_port(host)
        server.start()
        logger.info(f"Сервер запущен на {host}")
        server.wait_for_termination()
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    serve() 