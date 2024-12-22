INITIAL_TERMS = [
    {
        "name": "Микросервисы",
        "definition": "Архитектурный стиль, при котором приложение разбивается на небольшие автономные сервисы",
        "related_terms": ["Docker", "gRPC", "REST API"],
        "source": "Martin Fowler - Microservices Architecture",
        "relations": {
            "Docker": "реализуется с помощью",
            "gRPC": "взаимодействует через",
            "REST API": "взаимодействует через"
        }
    },
    {
        "name": "Docker",
        "definition": "Платформа для разработки, доставки и запуска приложений в контейнерах",
        "related_terms": ["Контейнеризация", "Docker Compose", "Микросервисы"],
        "source": "docs.docker.com",
        "relations": {
            "Контейнеризация": "является примером",
            "Docker Compose": "использует",
            "Микросервисы": "поддерживает"
        }
    },
    {
        "name": "Docker Compose",
        "definition": "Инструмент для определения и запуска многоконтейнерных Docker приложений",
        "related_terms": ["Docker", "Контейнеризация"],
        "source": "docs.docker.com/compose/",
        "relations": {
            "Docker": "является частью",
            "Контейнеризация": "реализует"
        }
    },
    {
        "name": "Контейнеризация",
        "definition": "Метод виртуализации, при котором приложение и его зависимости упаковываются в изолированный контейнер",
        "related_terms": ["Docker", "Docker Compose"],
        "source": "kubernetes.io/docs/concepts/containers/",
        "relations": {
            "Docker": "реализуется через",
            "Docker Compose": "использует"
        }
    },
    {
        "name": "REST API",
        "definition": "Архитектурный стиль взаимодействия компонентов распределённого приложения в сети",
        "related_terms": ["Микросервисы", "HTTP"],
        "source": "Roy Fielding's dissertation",
        "relations": {
            "Микросервисы": "используется в",
            "HTTP": "базируется на"
        }
    },
    {
        "name": "HTTP",
        "definition": "Протокол прикладного уровня передачи данных в сети Интернет",
        "related_terms": ["REST API", "gRPC"],
        "source": "ietf.org/rfc/rfc2616",
        "relations": {
            "REST API": "является основой",
            "gRPC": "используется в HTTP/2"
        }
    },
    {
        "name": "gRPC",
        "definition": "Высокопроизводительный фреймворк для RPC (удаленного вызова процедур)",
        "related_terms": ["Protocol Buffers", "HTTP", "Микросервисы"],
        "source": "grpc.io",
        "relations": {
            "Protocol Buffers": "использует",
            "HTTP": "базируется на HTTP/2",
            "Микросервисы": "применяется в"
        }
    },
    {
        "name": "Protocol Buffers",
        "definition": "Механизм сериализации структурированных данных от Google",
        "related_terms": ["gRPC", "Сериализация"],
        "source": "developers.google.com/protocol-buffers",
        "relations": {
            "gRPC": "используется в",
            "Сериализация": "является методом"
        }
    },
    {
        "name": "Сериализация",
        "definition": "Процесс перевода структуры данных в последовательность битов",
        "related_terms": ["Protocol Buffers"],
        "source": "wiki",
        "relations": {
            "Protocol Buffers": "реализуется через"
        }
    }
] 