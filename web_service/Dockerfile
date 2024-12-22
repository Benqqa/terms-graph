FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY web_service/package*.json /app/web_service/

WORKDIR /app/web_service
RUN npm install

WORKDIR /app

COPY protobufs/ /app/protobufs/
COPY web_service/ /app/web_service/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m grpc_tools.protoc -I ./protobufs \
    --python_out=./web_service \
    --grpc_python_out=./web_service \
    ./protobufs/dictionary.proto

WORKDIR /app/web_service

EXPOSE 5000

CMD ["python", "web_service.py"] 