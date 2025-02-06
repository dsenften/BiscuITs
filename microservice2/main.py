import os
import sys
import pika
import json
import time


def main():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=os.environ['RABBITMQ_HOST'],
                                       port=int(os.environ['RABBITMQ_PORT'])))
            channel = connection.channel()
            channel.queue_declare(queue='processing_queue')  # Queue von Microservice 1
            channel.queue_declare(queue='result_queue')      # Queue für UI
            break
        except pika.exceptions.AMQPConnectionError:
            print("Failed to connect to RabbitMQ. Retrying in 5 seconds...")
            time.sleep(5)

    def callback(ch, method, properties, body):
        try:
            # Parse the incoming message
            data = json.loads(body.decode())
            name = data.get('name', '')
            address = data.get('address', '')
            initial_result = data.get('initial_result', '')

            # Weitere Verarbeitung hier
            final_result = f"Analyse abgeschlossen für {name}:\n" \
                         f"Adresse: {address}\n" \
                         f"Details: {initial_result}"

            # Send final result back to UI
            channel.basic_publish(
                exchange='',
                routing_key='result_queue',
                body=final_result.encode()
            )
            print(f"Sent final result for {name}")

        except json.JSONDecodeError:
            error_msg = "Fehler: Ungültiges Nachrichtenformat"
            channel.basic_publish(
                exchange='',
                routing_key='result_queue',
                body=error_msg.encode()
            )
        except Exception as e:
            error_msg = f"Fehler bei der Verarbeitung: {str(e)}"
            channel.basic_publish(
                exchange='',
                routing_key='result_queue',
                body=error_msg.encode()
            )

    channel.basic_consume(
        queue='processing_queue',
        on_message_callback=callback,
        auto_ack=True
    )

    print('Microservice 2: Waiting for messages. To exit press CTRL+C')
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
