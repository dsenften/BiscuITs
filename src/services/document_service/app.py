import json
import os
from datetime import datetime

import pika
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

# Lade Umgebungsvariablen
load_dotenv()

app = Flask(__name__)

# Konfiguration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "doc", "docx"}

# Stelle sicher, dass der Upload-Ordner existiert
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max-limit


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def send_to_queue(filename, file_path):
    """Sendet Dokumenteninformationen an RabbitMQ"""
    try:
        # RabbitMQ Verbindung aufbauen
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv("RABBITMQ_HOST", "localhost"),
                port=int(os.getenv("RABBITMQ_PORT", 5672)),
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_USER", "guest"),
                    os.getenv("RABBITMQ_PASSWORD", "guest"),
                ),
            )
        )
        channel = connection.channel()

        # Queue deklarieren
        channel.queue_declare(queue="document_processor_input")

        # Nachricht erstellen
        message = {
            "filename": filename,
            "file_path": file_path,
            "timestamp": str(datetime.now()),
        }

        # Nachricht an die Queue senden
        channel.basic_publish(
            exchange="",
            routing_key="result_processor_input",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # macht Nachricht persistent
            ),
        )

        connection.close()
        return True
    except Exception as e:
        app.logger.error(f"Fehler beim Senden an RabbitMQ: {str(e)}")
        return False


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Endpunkt zum Hochladen von Dokumenten

    Returns:
        JSON mit Status und Nachricht
    """
    # Prüfe ob eine Datei im Request ist
    if "file" not in request.files:
        return (
            jsonify({"status": "error", "message": "Keine Datei im Request gefunden"}),
            400,
        )

    file = request.files["file"]

    # Wenn keine Datei ausgewählt wurde
    if file.filename == "":
        return jsonify({"status": "error", "message": "Keine Datei ausgewählt"}), 400

    # Prüfe ob die Datei erlaubt ist
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Speichere die Datei
        file.save(file_path)

        # Sende an RabbitMQ
        if send_to_queue(filename, file_path):
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Datei erfolgreich hochgeladen und zur Verarbeitung weitergeleitet",
                        "filename": filename,
                    }
                ),
                200,
            )
        else:
            # Lösche die Datei bei Fehler
            os.remove(file_path)
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Fehler beim Weiterleiten zur Verarbeitung",
                    }
                ),
                500,
            )

    return jsonify({"status": "error", "message": "Dateityp nicht erlaubt"}), 400


@app.route("/health", methods=["GET"])
def health_check():
    """
    Endpunkt für Health Checks
    """
    return jsonify({"status": "healthy", "service": "document_service"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
