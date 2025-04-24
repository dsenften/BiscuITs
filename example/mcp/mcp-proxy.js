/**
 * MCP-Proxy: Stellt einen HTTP-Server bereit, der mit einem MCP-Server über stdio kommuniziert
 * 
 * Verwendung:
 * node mcp-proxy.js <mcp-server-package>
 * 
 * Beispiel:
 * node mcp-proxy.js @modelcontextprotocol/server-sequential-thinking
 */

const express = require('express');
const { spawn } = require('child_process');
const bodyParser = require('body-parser');

// Konfiguration
const PORT = process.env.PORT || 8080;
const MCP_PACKAGE = process.argv[2];
const TIMEOUT_MS = 30000; // 30 Sekunden Timeout

if (!MCP_PACKAGE) {
  console.error('Fehler: MCP-Server-Paket muss als Argument angegeben werden');
  console.error('Beispiel: node mcp-proxy.js @modelcontextprotocol/server-sequential-thinking');
  process.exit(1);
}

// Express-App initialisieren
const app = express();
app.use(bodyParser.json());

// Puffer für stdout-Daten
let stdoutBuffer = [];

// MCP-Server als Subprozess starten
console.log(`Starte MCP-Server: ${MCP_PACKAGE}`);

// Prüfe, ob es sich um ein Playwright-MCP handelt
const isPlaywright = MCP_PACKAGE.includes('playwright');
const mcpProcess = isPlaywright
  ? spawn('node', [
      '/usr/local/lib/node_modules/@executeautomation/playwright-mcp-server/dist/index.js'
    ], { stdio: ['pipe', 'pipe', 'pipe'] })
  : spawn('npx', ['-y', MCP_PACKAGE], { stdio: ['pipe', 'pipe', 'pipe'] });

// Event-Handler für MCP-Server
mcpProcess.stdout.on('data', (data) => {
  const dataStr = data.toString().trim();
  console.log('MCP-Server Ausgabe:');
  console.log('- Raw Buffer:', data);
  console.log('- Als String:', dataStr);
  console.log('- Länge:', data.length);
  console.log('- Hex:', data.toString('hex'));
  stdoutBuffer.push(dataStr);
  
  // Puffer auf max. 100 Einträge begrenzen
  if (stdoutBuffer.length > 100) {
    stdoutBuffer.shift();
  }
});

mcpProcess.stderr.on('data', (data) => {
  console.error(`MCP-Server stderr: ${data}`);
});

mcpProcess.on('close', (code) => {
  console.log(`MCP-Server beendet mit Code ${code}`);
  process.exit(code);
});

// Anfrage-Handler
app.post('/chat', async (req, res) => {
  try {
    const message = req.body.message;
    console.log(`Anfrage erhalten: ${message}`);
    
    // Aktuelle Länge des Puffers merken
    const bufferLengthBefore = stdoutBuffer.length;
    
    // Parse die eingehende Nachricht
    const parsedMessage = JSON.parse(message);
    console.log('Parsed message:', parsedMessage);
    
    // Sende die Nachricht im MCP-Format
    const mcpMessage = JSON.stringify(parsedMessage) + '\n';
    console.log('Sende MCP Nachricht:', mcpMessage);
    mcpProcess.stdin.write(mcpMessage);
    
    // Warten und auf Antwort prüfen
    let responseData = null;
    const startTime = Date.now();
    
    // Warte auf Antwort mit Timeout
    for (let i = 0; i < 300; i++) { // 30 Sekunden mit 100ms Intervallen
      if (stdoutBuffer.length > bufferLengthBefore) {
        const newOutput = stdoutBuffer.slice(bufferLengthBefore).join('');
        console.log('Neue Ausgabe vom MCP-Server:', newOutput);
        
        // Versuche jede Zeile als JSON zu parsen
        const lines = newOutput.split('\n').filter(line => line.trim());
        for (const line of lines) {
          try {
            responseData = JSON.parse(line);
            if (responseData) {
              console.log('Gültige JSON-Antwort gefunden:', responseData);
              break;
            }
          } catch (e) {
            console.log('Keine gültige JSON in Zeile:', line);
          }
        }
        
        if (responseData) break;
      }
      
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    if (responseData) {
      console.log('Antwort gefunden:', responseData);
      res.json({ response: responseData });
    } else {
      // Timeout - trotzdem alle gesammelten Daten zurückgeben
      console.log('Timeout - gebe gesammelte Daten zurück');
      const allNewOutput = stdoutBuffer.slice(bufferLengthBefore).join('');
      res.json({ 
        response: allNewOutput || "Keine Antwort vom MCP-Server erhalten",
        warning: "Timeout beim Warten auf strukturierte Antwort"
      });
    }
  } catch (error) {
    console.error('Fehler bei Verarbeitung der Anfrage:', error);
    res.status(500).json({ 
      error: error.message,
      buffer: stdoutBuffer.join('') // Debug-Info
    });
  }
});

// Status-Endpunkt
app.get('/status', (req, res) => {
  res.json({
    status: 'running',
    mcpPackage: MCP_PACKAGE,
    recentOutput: stdoutBuffer.slice(-10) // Die letzten 10 Ausgaben
  });
});

// Server starten
app.listen(PORT, '0.0.0.0', () => {
  console.log(`MCP-Proxy läuft auf http://0.0.0.0:${PORT}`);
  console.log(`Verbunden mit MCP-Server: ${MCP_PACKAGE}`);
});
