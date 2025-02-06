import streamlit as st
import pika
import time
import json


def send_address(name, address):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        # Declare both queues
        channel.queue_declare(queue='address_queue')
        channel.queue_declare(queue='result_queue')

        # Create message as JSON
        message = json.dumps({
            "name": name,
            "address": address
        })

        channel.basic_publish(exchange='', routing_key='address_queue', body=message)
        connection.close()
        return True
    except Exception as e:
        st.error(f"Fehler beim Senden: {str(e)}")
        return False


def wait_for_result(timeout=30):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='result_queue')

        start_time = time.time()
        while time.time() - start_time < timeout:
            method_frame, properties, body = channel.basic_get(queue='result_queue', auto_ack=True)
            if method_frame:
                channel.close()
                connection.close()
                return body.decode()
            time.sleep(0.1)

        channel.close()
        connection.close()
        return None
    except Exception as e:
        st.error(f"Fehler beim Empfangen: {str(e)}")
        return None


def main():
    st.title("Adress-Info-App")

    with st.form(key='address_form'):
        name = st.text_input("Name")
        plz = st.text_input("PLZ")
        ort = st.text_input("Ort")
        submit_button = st.form_submit_button(label='Senden')

    if submit_button:
        if not name or not plz or not ort:
            st.warning("Bitte füllen Sie alle Felder aus.")
            return

        address = f"{plz} {ort}"
        if send_address(name, address):
            with st.spinner('Warte auf Antwort...'):
                result = wait_for_result()
                if result:
                    st.success(result)
                else:
                    st.error("Zeitüberschreitung bei der Antwort.")


if __name__ == '__main__':
    main()
