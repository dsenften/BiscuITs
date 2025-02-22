import os
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
            channel.queue_declare(queue='address_queue')
            channel.queue_declare(queue='processing_queue')  # Neue Queue für Microservice 2
            break
        except pika.exceptions.AMQPConnectionError:
            print("Failed to connect to RabbitMQ. Retrying in 5 seconds...")
            time.sleep(5)

    def callback(ch, method, properties, body):
        try:
            # Parse JSON message
            data = json.loads(body.decode())
            name = data.get('name', '')
            address = data.get('address', '')

            # Initial processing
            initial_result = f"Beginne Analyse für {name} mit Adresse: {address}"
            print(f"Initial processing: {initial_result}")

            # Send to microservice 2 for further processing
            channel.basic_publish(
                exchange='',
                routing_key='processing_queue',
                body=json.dumps({
                    'name': name,
                    'address': address,
                    'initial_result': initial_result
                })
            )
            print(f"Sent to processing for {name}")

        except json.JSONDecodeError:
            error_msg = "Fehler: Ungültiges Nachrichtenformat"
            print(f"Error: {error_msg}")
        except Exception as e:
            print(f"Error processing message: {str(e)}")

    channel.basic_consume(
        queue='address_queue',
        on_message_callback=callback,
        auto_ack=True
    )

    print('Microservice 1: Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    main()
