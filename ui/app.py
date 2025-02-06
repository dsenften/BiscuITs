#  Released under MIT License
#
#  Copyright (©) 2025. Talent Factory GmbH
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#  of the Software, and to permit persons to whom the Software is furnished to
#  do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NON INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.

import streamlit as st
import pika
import time


def send_address(name, address):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='address_queue')
    message = f"{name},{address}"
    channel.basic_publish(exchange='', routing_key='address_queue', body=message)
    connection.close()


def main():
    st.title("Adress-Info-App")

    with st.form(key='address_form'):
        name = st.text_input("Name")
        plz = st.text_input("PLZ")
        ort = st.text_input("Ort")

        submit_button = st.form_submit_button(label='Senden')

    if submit_button:
        address = f"{plz} {ort}"
        send_address(name, address)

        with st.spinner('Warte auf Antwort...'):
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='result_queue')

            for method_frame, properties, body in channel.consume('result_queue'):
                result = body.decode()
                st.write(result)
                break

            channel.close()


if __name__ == '__main__':
    main()
