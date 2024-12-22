FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY protobufs/ /app/protobufs/
COPY dictionary_service/ /app/dictionary_service/
COPY requirements.txt /app/

COPY dictionary_service/initial_data.py /app/dictionary_service/

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m grpc_tools.protoc -I ./protobufs \
    --python_out=. \
    --grpc_python_out=. \
    ./protobufs/dictionary.proto

ENV PYTHONPATH=/app

CMD ["python", "-m", "dictionary_service.server"] 