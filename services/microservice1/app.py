import json
import threading
import uuid

import pika
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-Memory-Speicher für Antworten, thread-sicher gestaltet.
results = {}
results_lock = threading.Lock()

RABBITMQ_HOST = 'rabbitmq'
REQUEST_QUEUE = 'request_queue'
RESPONSE_QUEUE = 'response_queue'


def rabbitmq_response_listener():
    """Hört auf die Response-Queue und speichert Ergebnisse."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RESPONSE_QUEUE, durable=True)

    def callback(ch, method, properties, body):
        data = json.loads(body.decode())
        correlation_id = data.get("correlation_id")
        result_text = data.get("result")
        with results_lock:
            results[correlation_id] = result_text
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=RESPONSE_QUEUE, on_message_callback=callback)
    channel.start_consuming()


# Startet den RabbitMQ-Listener in einem Hintergrundthread
listener_thread = threading.Thread(target=rabbitmq_response_listener, daemon=True)
listener_thread.start()


@app.route('/submit', methods=['POST'])
def submit():
    """Nimmt die Anfrage von der UI entgegen und leitet sie in die Request-Queue weiter."""
    content = request.get_json()
    if not content or 'name' not in content or 'address' not in content:
        return jsonify({'error': 'Fehlende Parameter'}), 400

    # Erzeuge eindeutige ID für diese Anfrage
    correlation_id = str(uuid.uuid4())
    message = {
        "correlation_id": correlation_id,
        "name": content["name"],
        "address": content["address"]
    }

    # Sende die Nachricht an die Request Queue
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=REQUEST_QUEUE, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=REQUEST_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # persistente Nachricht
            )
        )
        connection.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'correlation_id': correlation_id}), 202


@app.route('/result/<correlation_id>', methods=['GET'])
def get_result(correlation_id):
    """Gibt das Ergebnis zur angegebenen Korrelation-ID zurück."""
    with results_lock:
        if correlation_id in results:
            return jsonify({'result': results.pop(correlation_id)}), 200
    # Ergebnis noch nicht verfügbar
    return jsonify({'status': 'pending'}), 202


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
