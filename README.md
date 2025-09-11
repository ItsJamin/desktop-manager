# Project Setup

This project allows for voice-controlled interaction with an Ollama language model.

## Prerequisites

- Python 3.x
- Ollama installed and running (https://ollama.ai/download)
- FFmpeg installed and added to your system's PATH (https://ffmpeg.org/download.html)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ItsJamin/desktop-manager.git
    cd desktop-manager
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Note: `python-dotenv` will be added to `requirements.txt` if not already present.)

## Configuration

Create a `.env` file in the root directory of the project with the following content:

```
OLLAMA_MODEL="deepseek-r1:8b"
OLLAMA_BASE_URL="http://localhost:11434"
```

-   `OLLAMA_MODEL`: Specify the Ollama model you want to use (e.g., "llama2", "deepseek-r1:8b").
-   `OLLAMA_BASE_URL`: The URL where your Ollama instance is running.

## Running the Application

### Voice Chat Mode (Default)

To start the application in voice chat mode:

```bash
python main.py
```

-   Press and hold `ctrl+space` to record your voice message.
-   Release the key to transcribe and send to Ollama.
-   Press `c` to clear conversation history.
-   Press `esc` to exit.

### Text-Only Chat Mode

To start the application in text-only chat mode:

```bash
python main.py --text-only
```

-   Type your messages and press Enter to send.
-   Type `clear` to clear conversation history.
-   Type `quit` or `exit` to quit.

## Modules

-   `ollama_chat.py`: Contains the `OllamaChat` class for interacting with the Ollama API. It handles sending messages, managing conversation history, and checking the Ollama connection.
-   `voice_input.py`: Provides the `VoiceRecorder` class for capturing audio input from the microphone. It handles starting and stopping recordings and processing raw audio data.
-   `main.py`: The main entry point of the application. It orchestrates the `OllamaChat` and `VoiceRecorder` classes, handles user input (voice or text), transcribes audio using the Whisper model, and manages the overall chat flow.
