import os
import sys
import pika
import json
import time
import logging
from dotenv import load_dotenv

# Logger konfigurieren
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Lade Umgebungsvariablen
load_dotenv()


def main():
    # RabbitMQ-Konfiguration aus Umgebungsvariablen laden
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
    rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
    rabbitmq_pass = os.getenv('RABBITMQ_PASSWORD', 'guest')

    logger.info(f"Verbindung zu RabbitMQ auf {rabbitmq_host}:{rabbitmq_port} wird hergestellt...")

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbitmq_host,
                    port=rabbitmq_port,
                    credentials=pika.PlainCredentials(
                        rabbitmq_user,
                        rabbitmq_pass
                    )
                ))
            channel = connection.channel()
            channel.queue_declare(queue='result_processor_input')  # Queue für eingehende Verarbeitungsergebnisse
            channel.queue_declare(queue='ui_updates')  # Queue für UI
            logger.info("RabbitMQ-Verbindung erfolgreich hergestellt")
            break
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Verbindung zu RabbitMQ fehlgeschlagen: {str(e)}")
            logger.info("Wiederversuch in 5 Sekunden...")
            time.sleep(5)

    def callback(ch, method, properties, body):
        try:
            # Parse the incoming message
            logger.info("Nachricht empfangen, wird verarbeitet...")
            data = json.loads(body.decode())

            # Extrahiere Daten mit Standardwerten
            name = data.get('name', 'Unbekannt')
            address = data.get('address', 'Keine Adresse angegeben')
            initial_result = data.get('initial_result', 'Keine Details verfügbar')
            document_id = data.get('document_id', '')

            # Weitere Verarbeitung hier
            final_result = {
                "name": name,
                "address": address,
                "details": initial_result,
                "document_id": document_id,
                "timestamp": time.time(),
                "status": "completed"
            }

            # Send final result back to UI as JSON
            channel.basic_publish(
                exchange='',
                routing_key='ui_updates',
                body=json.dumps(final_result),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )
            logger.info(f"Analyseergebnis für '{name}' an UI gesendet")

        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Parsen der JSON-Nachricht: {str(e)}")
            error_msg = {
                "status": "error",
                "message": "Ungültiges Nachrichtenformat",
                "details": str(e)
            }
            channel.basic_publish(
                exchange='',
                routing_key='ui_updates',
                body=json.dumps(error_msg),
                properties=pika.BasicProperties(content_type='application/json')
            )
        except Exception as e:
            logger.error(f"Unerwarteter Fehler bei der Verarbeitung: {str(e)}")
            error_msg = {
                "status": "error",
                "message": "Fehler bei der Verarbeitung",
                "details": str(e)
            }
            channel.basic_publish(
                exchange='',
                routing_key='ui_updates',
                body=json.dumps(error_msg),
                properties=pika.BasicProperties(content_type='application/json')
            )

    channel.basic_consume(
        queue='result_processor_input',
        on_message_callback=callback,
        auto_ack=True
    )

    logger.info('Result Processor Service: Warte auf Nachrichten. Drücke CTRL+C zum Beenden')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
