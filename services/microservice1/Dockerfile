FROM python:3.9-slim

WORKDIR /app

# Installiere benötigte Pakete
RUN pip install flask pika

# Kopiere den Code in den Container
COPY app.py .

EXPOSE 5001

CMD ["python", "app.py"]
