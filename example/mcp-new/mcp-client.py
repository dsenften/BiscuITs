#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP-Client für die Kommunikation mit dem MCP-Server
"""

import asyncio
import json
from datetime import datetime

import httpx


async def main():
    """Hauptfunktion für den MCP-Client"""
    # Server-URL mit Port 8081
    server_url = "http://127.0.0.1:8081"
    
    # Verbindung zum MCP-Server herstellen
    print("Verbinde mit dem MCP-Server...")
    async with httpx.AsyncClient() as client:
        # Server-Status prüfen
        try:
            response = await client.get(f"{server_url}/")
            if response.status_code == 200:
                print("Verbindung hergestellt!")
            else:
                print(f"Fehler: Server antwortet mit Status {response.status_code}")
                return
        except httpx.RequestError as e:
            print(f"Fehler: Verbindung zum Server fehlgeschlagen - {e}")
            return
        
        # Verfügbare Funktionen anzeigen
        try:
            response = await client.get(f"{server_url}/tools")
            tools = response.json()
            print("\nVerfügbare Tools:")
            for tool in tools:
                print(f"- {tool['name']}: {tool['description']}")
        except Exception as e:
            print(f"Fehler beim Abrufen der Tools: {e}")
        
        # Lokale Zeit abrufen
        print("\nRufe lokale Zeit ab...")
        try:
            response = await client.post(
                f"{server_url}/tools/get_local_time",
                json={}
            )
            time_result = response.json()
            print(f"Lokale Zeit: {time_result}")
        except Exception as e:
            print(f"Fehler beim Abrufen der lokalen Zeit: {e}")
        
        # Addition durchführen
        a, b = 42, 23
        print(f"\nBerechne {a} + {b}...")
        try:
            response = await client.post(
                f"{server_url}/tools/add",
                json={"a": a, "b": b}
            )
            add_result = response.json()
            print(f"Ergebnis: {add_result}")
        except Exception as e:
            print(f"Fehler bei der Addition: {e}")
        
        # Personalisierte Begrüßung abrufen
        name = "Daniel"
        print(f"\nRufe Begrüßung für {name} ab...")
        try:
            response = await client.get(f"{server_url}/resources/greeting/{name}")
            greeting = response.text
            print(f"Begrüßung: {greeting}")
        except Exception as e:
            print(f"Fehler beim Abrufen der Begrüßung: {e}")


if __name__ == "__main__":
    asyncio.run(main())
