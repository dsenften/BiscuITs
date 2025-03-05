import streamlit as st
import pika
import time
import json
import os
from dotenv import load_dotenv
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Umgebungsvariablen laden
load_dotenv()

# RabbitMQ-Konfiguration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")


def get_rabbitmq_connection():
    """Stellt eine Verbindung zu RabbitMQ her mit Retry-Mechanismus"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=pika.PlainCredentials(
                        RABBITMQ_USER,
                        RABBITMQ_PASSWORD
                    ),
                    heartbeat=600
                )
            )
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Verbindung zu RabbitMQ fehlgeschlagen (Versuch {attempt+1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
            else:
                raise
    
    raise Exception("Konnte keine Verbindung zu RabbitMQ herstellen")


def send_address(name, address):
    """Sendet Adressdaten an die RabbitMQ-Queue"""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        # Queues deklarieren
        channel.queue_declare(queue='address_processing')
        channel.queue_declare(queue='ui_updates')

        # Nachricht als JSON erstellen
        message = json.dumps({
            "name": name,
            "address": address,
            "timestamp": time.time()
        })

        # Nachricht an die Queue senden
        channel.basic_publish(
            exchange='', 
            routing_key='address_processing', 
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Nachricht persistent machen
                content_type='application/json'
            )
        )
        
        logger.info(f"Adressdaten für '{name}' erfolgreich gesendet")
        connection.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Senden der Adressdaten: {str(e)}")
        st.error(f"Fehler beim Senden: {str(e)}")
        return False


def test_send_address():
    """Testfälle für die send_address Funktion"""
    import unittest
    from unittest.mock import patch, MagicMock

    class TestSendAddress(unittest.TestCase):
        @patch('app.get_rabbitmq_connection')
        def test_send_address_success(self, mock_get_connection):
            # Mock-Objekte einrichten
            mock_connection = MagicMock()
            mock_channel = MagicMock()
            mock_connection.channel.return_value = mock_channel
            mock_get_connection.return_value = mock_connection
            
            # Funktion aufrufen
            result = send_address("Test Kunde", "Teststraße 1, 12345 Teststadt")
            
            # Assertions
            self.assertTrue(result)
            mock_get_connection.assert_called_once()
            mock_connection.channel.assert_called_once()
            mock_channel.queue_declare.assert_any_call(queue='address_processing')
            mock_channel.queue_declare.assert_any_call(queue='ui_updates')
            mock_channel.basic_publish.assert_called_once()
            mock_connection.close.assert_called_once()
        
        @patch('app.get_rabbitmq_connection')
        def test_send_address_with_empty_name(self, mock_get_connection):
            # Test mit leerem Namen
            result = send_address("", "Teststraße 1, 12345 Teststadt")
            # Funktion sollte trotzdem versuchen, Daten zu senden
            self.assertTrue(result)
            mock_get_connection.assert_called_once()
        
        @patch('app.get_rabbitmq_connection')
        def test_send_address_with_empty_address(self, mock_get_connection):
            # Test mit leerer Adresse
            result = send_address("Test Kunde", "")
            # Funktion sollte trotzdem versuchen, Daten zu senden
            self.assertTrue(result)
            mock_get_connection.assert_called_once()
        
        @patch('app.get_rabbitmq_connection', side_effect=Exception("Connection error"))
        @patch('app.st')
        def test_send_address_connection_error(self, mock_st, mock_get_connection):
            # Test mit Verbindungsfehler
            result = send_address("Test Kunde", "Teststraße 1, 12345 Teststadt")
            
            # Assertions
            self.assertFalse(result)
            mock_get_connection.assert_called_once()
            mock_st.error.assert_called_once()
        
        @patch('app.get_rabbitmq_connection')
        def test_send_address_message_structure(self, mock_get_connection):
            # Mock-Objekte einrichten
            mock_connection = MagicMock()
            mock_channel = MagicMock()
            mock_connection.channel.return_value = mock_channel
            mock_get_connection.return_value = mock_connection
            
            # Funktion aufrufen
            name = "Test Kunde"
            address = "Teststraße 1, 12345 Teststadt"
            send_address(name, address)
            
            # Nachrichtenstruktur prüfen
            call_args = mock_channel.basic_publish.call_args
            _, kwargs = call_args
            message = json.loads(kwargs["body"])
            
            self.assertEqual(message["name"], name)
            self.assertEqual(message["address"], address)
            self.assertIn("timestamp", message)
            
    # Weitere Tests könnten hinzugefügt werden


def wait_for_result(timeout=30):
    """Wartet auf das Ergebnis aus der RabbitMQ-Queue"""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue='ui_updates')

        start_time = time.time()
        while time.time() - start_time < timeout:
            method_frame, properties, body = channel.basic_get(queue='ui_updates', auto_ack=True)
            if method_frame:
                connection.close()
                
                # JSON-Nachricht parsen
                try:
                    result = json.loads(body.decode())
                    logger.info(f"Ergebnis empfangen: {result}")
                    return result
                except json.JSONDecodeError:
                    logger.warning("Empfangene Nachricht ist kein gültiges JSON")
                    return {"status": "error", "message": "Ungültiges Antwortformat"}
            
            time.sleep(0.5)

        connection.close()
        logger.warning("Zeitüberschreitung beim Warten auf Ergebnis")
        return None
    except Exception as e:
        logger.error(f"Fehler beim Empfangen des Ergebnisses: {str(e)}")
        st.error(f"Fehler beim Empfangen: {str(e)}")
        return None


def main():
    st.title("BiscuITs - Dokumenten- und Adressverarbeitung")
    
    # Tabs für verschiedene Funktionen
    tab1, tab2 = st.tabs(["Adressdaten", "Dokumente"])
    
    # Tab für Adressdaten
    with tab1:
        st.header("Adressdaten verarbeiten")
        
        with st.form(key='address_form'):
            name = st.text_input("Name")
            plz = st.text_input("PLZ")
            ort = st.text_input("Ort")
            strasse = st.text_input("Straße", "")
            submit_button = st.form_submit_button(label='Adresse senden')

        if submit_button:
            if not name or not plz or not ort:
                st.warning("Bitte füllen Sie die Pflichtfelder aus (Name, PLZ, Ort).")
                return

            # Vollständige Adresse zusammenbauen
            address = f"{strasse}, {plz} {ort}"
            
            if send_address(name, address):
                with st.spinner('Verarbeite Adressdaten...'):
                    result = wait_for_result()
                    if result:
                        # Ergebnis als JSON formatiert anzeigen
                        if isinstance(result, dict):
                            if result.get("status") == "error":
                                st.error(result.get("message", "Ein Fehler ist aufgetreten"))
                            else:
                                st.success("Adressdaten erfolgreich verarbeitet")
                                
                                # Ergebnisse anzeigen
                                st.json(result)
                        else:
                            st.success(result)
                    else:
                        st.error("Zeitüberschreitung bei der Verarbeitung der Adressdaten.")
    
    # Tab für Dokumente
    with tab2:
        st.header("Dokumente hochladen")
        
        uploaded_file = st.file_uploader("Dokument hochladen", 
                                         type=['pdf', 'txt', 'doc', 'docx', 'jpg', 'png'])
        
        if uploaded_file is not None:
            st.info(f"Datei: {uploaded_file.name}")
            
            if st.button("Dokument verarbeiten"):
                # Hier würde normaler Code zum Senden des Dokuments stehen
                # Derzeit nur Platzhalter
                st.success("Dokument wurde hochgeladen und zur Verarbeitung gesendet.")
                st.info("Die Dokumentverarbeitung ist noch in Entwicklung.")


if __name__ == "__main__":
    # Beim direkten Ausführen dieses Skripts laufen die Tests
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        import unittest
        unittest.main(argv=['first-arg-is-ignored'])
    else:
        main()
