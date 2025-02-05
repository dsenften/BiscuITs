FROM python:3.9-slim

WORKDIR /app

RUN pip install pika

COPY worker.py .

CMD ["python", "worker.py"]
