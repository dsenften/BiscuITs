import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import docling

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
except Exception:
    # Collection existiert bereits
    pass

class DocumentRequest(BaseModel):
    document_id: str

@app.post("/process")
async def process_document(request: DocumentRequest):
    try:
        # Dokument vom document_service abrufen
        response = requests.get(f"{DOCUMENT_SERVICE_URL}/documents/{request.document_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document_data = response.json()
        document_content = document_data.get("content", "")
        
        # Dokument mit Docling verarbeiten
        doc = docling.Document(document_content)
        doc.process()
        
        # Embedding erstellen
        embedding = doc.embedding
        
        # In Qdrant speichern
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=hash(request.document_id),  # Eindeutige ID
                    vector=embedding,
                    payload={
                        "document_id": request.document_id,
                        "content": document_content,
                        "summary": doc.summary,
                        "keywords": doc.keywords,
                        "sentiment": doc.sentiment
                    }
                )
            ]
        )
        
        return {
            "status": "success",
            "document_id": request.document_id,
            "summary": doc.summary,
            "keywords": doc.keywords,
            "sentiment": doc.sentiment
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
