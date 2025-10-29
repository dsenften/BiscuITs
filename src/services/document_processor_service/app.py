import hashlib
import logging
import os

import requests
from docling_core.document import Document as DoclingDocument
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Umgebungsvariablen laden
load_dotenv()

app = FastAPI()

# Konfiguration
DOCUMENT_SERVICE_URL = os.getenv("DOCUMENT_SERVICE_URL", "http://localhost:8000")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "documents"

# Qdrant Client initialisieren
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Stelle sicher, dass die Collection existiert
try:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    )
    logger.info(f"Collection '{COLLECTION_NAME}' erfolgreich erstellt")
except Exception as e:
    logger.info(f"Collection existiert bereits oder Fehler: {str(e)}")
    pass


class DocumentRequest(BaseModel):
    document_id: str


@app.post("/process")
async def process_document(request: DocumentRequest):
    try:
        # Dokument vom document_service abrufen
        response = requests.get(
            f"{DOCUMENT_SERVICE_URL}/documents/{request.document_id}"
        )
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Document not found")

        document_data = response.json()
        document_content = document_data.get("content", "")

        try:
            # Dokument mit Docling verarbeiten
            doc = DoclingDocument(document_content)
            doc.process()
            logger.info(f"Dokument {request.document_id} erfolgreich verarbeitet")

            # Embedding erstellen
            embedding = doc.embedding

            # Deterministischen Hash erstellen
            doc_id_hash = int(
                hashlib.md5(request.document_id.encode()).hexdigest(), 16
            ) % (10**10)

            # In Qdrant speichern
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=doc_id_hash,  # Deterministische ID
                        vector=embedding,
                        payload={
                            "document_id": request.document_id,
                            "content": document_content,
                            "summary": doc.summary if hasattr(doc, "summary") else "",
                            "keywords": (
                                doc.keywords if hasattr(doc, "keywords") else []
                            ),
                            "sentiment": (
                                doc.sentiment
                                if hasattr(doc, "sentiment")
                                else "neutral"
                            ),
                        },
                    )
                ],
            )
            logger.info(f"Dokument {request.document_id} in Qdrant gespeichert")
        except AttributeError as e:
            logger.error(f"Attributfehler bei Docling-Verarbeitung: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Docling-API-Fehler: {str(e)}")
        except Exception as e:
            logger.error(f"Fehler bei der Dokumentverarbeitung: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Verarbeitungsfehler: {str(e)}"
            )

        return {
            "status": "success",
            "document_id": request.document_id,
            "summary": doc.summary if hasattr(doc, "summary") else "",
            "keywords": doc.keywords if hasattr(doc, "keywords") else [],
            "sentiment": doc.sentiment if hasattr(doc, "sentiment") else "neutral",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
