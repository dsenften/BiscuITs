# server.py
import logging
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import PlainTextResponse
from uvicorn import run as uvicorn_run

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FastAPI-App erstellen
app = FastAPI(title="Zeit-Demo-Server")


# Modelle für die API
class AddRequest(BaseModel):
    a: int
    b: int


class EmptyRequest(BaseModel):
    pass


# Routen definieren
@app.get("/")
async def root():
    return {"status": "ok", "message": "Zeit-Demo-Server läuft"}


@app.get("/tools")
async def list_tools():
    return [
        {"name": "add", "description": "Add two numbers"},
        {"name": "get_local_time", "description": "Get the current time in local timezone (CEST/UTC+2)"}
    ]


@app.post("/tools/add")
async def add(request: AddRequest):
    return request.a + request.b


@app.post("/tools/get_local_time")
async def get_local_time(request: EmptyRequest = None):
    now = datetime.now().astimezone()
    return now.strftime("%H:%M:%S %Z (%d.%m.%Y)")


@app.get("/resources/greeting/{name}", response_class=PlainTextResponse)
async def get_greeting(name: str):
    now = datetime.now().astimezone()
    hour = now.hour

    if 5 <= hour < 12:
        greeting = "Guten Morgen"
    elif 12 <= hour < 18:
        greeting = "Guten Tag"
    else:
        greeting = "Guten Abend"

    return f"{greeting}, {name}! Es ist jetzt {now.strftime('%H:%M:%S')} Uhr."


# Starte den FastAPI-Server, wenn das Skript direkt ausgeführt wird
if __name__ == "__main__":
    # Starte den Server
    # Verwende Port 8081 statt 8080, um Konflikte zu vermeiden
    port = 8081
    logger.info(f"Zeit-Demo-Server wird gestartet auf http://127.0.0.1:{port}")
    logger.info("Drücken Sie STRG+C, um den Server zu beenden")
    try:
        # Uvicorn starten
        uvicorn_run(
            "mcp-server:app",  # Importpfad zur FastAPI-App
            host="127.0.0.1",
            port=port,
            reload=False,  # Kein automatisches Neuladen
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server wird beendet...")
    except Exception as e:
        logger.error(f"Fehler beim Starten des Servers: {e}")
    finally:
        logger.info("Server beendet.")
