import time
import json
import pika

RABBITMQ_HOST = 'rabbitmq'
REQUEST_QUEUE = 'request_queue'
RESPONSE_QUEUE = 'response_queue'


def process_request(message):
    """
    Simuliert eine GPT-4o Anfrage anhand des übermittelten Orts.
    Hier kannst du die echte GPT-4o-Integration einbauen.
    """
    address = message.get("address", {})
    # Wir gehen davon aus, dass address ein Dictionary mit 'ort' ist. Alternativ kann hier auch ein String stehen.
    ort = address.get("ort") if isinstance(address, dict) else address
    # Dummy-Antwort: In einer echten Implementierung würde hier der GPT-4o API-Aufruf stehen.
    result_text = f"Informationen zu {ort}: Dies ist eine simulierte Antwort."
    return result_text


def callback(ch, method, properties, body):
    message = json.loads(body.decode())
    correlation_id = message.get("correlation_id")
    print(f"Verarbeite Nachricht mit Correlation-ID: {correlation_id}")

    # Simuliere eine längere Verarbeitung
    time.sleep(5)

    result_text = process_request(message)
    response = {
        "correlation_id": correlation_id,
        "result": result_text
    }

    # Sende die Antwort an die Response Queue
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RESPONSE_QUEUE, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=RESPONSE_QUEUE,
        body=json.dumps(response),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )
    connection.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Antwort gesendet für Correlation-ID: {correlation_id}")


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=REQUEST_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=REQUEST_QUEUE, on_message_callback=callback)

    print("Worker wartet auf Nachrichten...")
    channel.start_consuming()


if __name__ == '__main__':
    main()
