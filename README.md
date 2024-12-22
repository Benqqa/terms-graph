# Глоссарий терминов с визуализацией

## Описание
Сервис представляет собой систему управления терминами с возможностью визуализации связей между ними. Система состоит из двух основных компонентов:
- gRPC-сервис для управления данными
- Веб-интерфейс для взаимодействия с пользователем

## Архитектура
- gRPC для взаимодействия между сервисами
- Flask для веб-интерфейса
- SQLite для хранения данных
- Cytoscape.js для визуализации графа терминов

## Процесс развертывания

### Требования
- Docker
- Docker Compose

### Шаги развертывания

1. Клонирование репозитория:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Сборка и запуск контейнеров:
```bash
docker compose up --build
```

3. Проверка статуса контейнеров:
```bash
docker compose ps
```

Ожидаемый результат:
```
NAME                COMMAND                  SERVICE             STATUS              PORTS
lab8-dictionary-1   "python -m dictionar…"   dictionary          running             0.0.0.0:50051->50051/tcp
lab8-web-1         "python web_service.…"    web                running             0.0.0.0:5000->5000/tcp
```

## Демонстрация работы

### 1. Доступ к веб-интерфейсу
После успешного запуска, веб-интерфейс доступен по адресу: http://localhost:5000

### 2. Основные функции

#### Просмотр списка терминов
- Перейдите на главную страницу
- Вы увидите список всех терминов с их определениями
- Термины отсортированы по алфавиту

#### Добавление нового термина
1. Нажмите кнопку "Добавить термин"
2. Заполните форму:
   - Название термина
   - Определение
   - Источник (опционально)
   - Связанные термины (опционально)
3. Нажмите "Создать"

#### Редактирование термина
1. Найдите нужный термин в списке
2. Нажмите кнопку редактирования (иконка карандаша)
3. Внесите изменения
4. Нажмите "Сохранить"

#### Удаление термина
1. Найдите нужный термин в списке
2. Нажмите кнопку удаления (иконка корзины)
3. Подтвердите удаление

#### Визуализация связей
1. Перейдите на вкладку "Визуализация"
2. Вы увидите интерактивный граф терминов:
   - Зеленые узлы - основные термины
   - Синие узлы - связанные термины
   - Стрелки показывают связи между терминами
3. Возможности интерактива:
   - Перетаскивание узлов
   - Масштабирование колесиком мыши
   - Клик по узлу для просмотра информации

### 3. Работа с API

Сервис предоставляет REST API для интеграции:

#### Получение списка терминов
```bash
curl http://localhost:5000/api/terms
```

#### Добавление термина
```bash
curl -X POST http://localhost:5000/api/terms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новый термин",
    "definition": "Определение термина",
    "source": "Источник",
    "related_terms": ["Связанный термин"],
    "relations": {"Связанный термин": "связан с"}
  }'
```

#### Обновление термина
```bash
curl -X PUT http://localhost:5000/api/terms/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Обновленный термин",
    "definition": "Новое определение"
  }'
```

#### Удаление термина
```bash
curl -X DELETE http://localhost:5000/api/terms/1
```

## Остановка сервиса

Для остановки сервиса выполните:
```bash
docker compose down
```

Для полной очистки (включая базу данных):
```bash
docker compose down -v
rm -f dictionary.db
```