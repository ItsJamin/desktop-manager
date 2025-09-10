# Desktop Manager - Voice to Ollama Chat

Ein Python-Programm, das Spracheingaben über Whisper transkribiert und diese an Ollama weiterleitet für KI-gestützte Unterhaltungen.

## Features

- **Spracheingabe**: Aufnahme über Hotkey (Ctrl+Space)
- **Speech-to-Text**: Automatische Transkription mit OpenAI Whisper
- **Ollama Integration**: Direkte Kommunikation mit lokalen Ollama-Modellen
- **Konversationshistorie**: Behält den Gesprächskontext bei
- **Flexibel**: Unterstützt verschiedene Ollama-Modelle
- **Text-Modus**: Optional auch ohne Spracheingabe nutzbar

## Voraussetzungen

### Software
- Python 3.7+
- [Ollama](https://ollama.ai/) installiert und laufend
- FFmpeg (für Whisper Audio-Verarbeitung)

### Python-Abhängigkeiten
```bash
pip install -r requirements.txt
```

## Installation

1. Repository klonen oder Dateien herunterladen
2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
3. Ollama installieren und starten:
   ```bash
   # Ollama installieren (siehe https://ollama.ai/)
   ollama serve
   ```
4. Ein Modell herunterladen (z.B.):
   ```bash
   ollama pull llama2
   ```

## Verwendung

### Voice-Chat Modus (Standard)
```bash
python ollama_chat.py
```

**Steuerung:**
- `Ctrl+Space` gedrückt halten: Aufnahme starten
- `Ctrl+Space` loslassen: Aufnahme beenden und an Ollama senden
- `C` drücken: Konversationshistorie löschen
- `ESC` drücken: Programm beenden

### Text-Chat Modus
```bash
python ollama_chat.py --text-only
```

### Erweiterte Optionen
```bash
# Anderes Modell verwenden
python ollama_chat.py --model llama3

# Andere Ollama-URL
python ollama_chat.py --url http://192.168.1.100:11434

# Alle Optionen anzeigen
python ollama_chat.py --help
```

## Programmstruktur

### `voice_input.py`
- Ursprüngliches Voice-Recording-Modul
- Verwendet Whisper für Speech-to-Text
- Hotkey-basierte Aufnahmesteuerung

### `ollama_chat.py`
- Hauptprogramm mit Ollama-Integration
- Zwei Hauptklassen:
  - `OllamaChat`: Direkte Ollama-Kommunikation
  - `VoiceToOllamaChat`: Integration von Voice-Input und Ollama

## Funktionsweise

1. **Spracheingabe**: Nutzer hält Ctrl+Space gedrückt und spricht
2. **Transkription**: Audio wird mit Whisper zu Text konvertiert
3. **Ollama-Anfrage**: Text wird an lokales Ollama-Modell gesendet
4. **Antwort**: KI-Antwort wird in der Konsole angezeigt
5. **Kontext**: Gesprächshistorie wird für Folgenachrichten beibehalten

## Fehlerbehebung

### Ollama-Verbindungsfehler
- Prüfen ob Ollama läuft: `ollama serve`
- Verfügbare Modelle prüfen: `ollama list`
- Firewall/Port 11434 prüfen

### Audio-Probleme
- FFmpeg installiert? `ffmpeg -version`
- Mikrofon-Berechtigungen prüfen
- Audio-Gerät in Systemeinstellungen prüfen

### Whisper-Modell-Download
- Beim ersten Start wird das Whisper-Modell heruntergeladen
- Internetverbindung erforderlich
- Modell wird in temporärem Verzeichnis gespeichert

## Anpassungen

### Anderes Whisper-Modell
In `voice_input.py` Zeile ändern:
```python
self.model = whisper.load_model("base")  # tiny, base, small, medium, large
```

### Anderer Hotkey
```python
recorder = VoiceRecorder(hotkey="ctrl+alt+space")
```

### Ollama-Parameter anpassen
```python
chat = OllamaChat(model="llama3", base_url="http://localhost:11434")
```

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
