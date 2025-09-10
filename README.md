# Requirements

Must use Python 3.11
Follow design principles like modularization, KISS, virtual environment, etc.

# Plan

## Step 1

- build a program which takes voice input on button press (alt+space)   
- print out the said stuff  
- use openai-whisper    

## Step 2 (flesh out before doing)

- define a set of desktop actions via jsons
- use local ollama to interpret what was said.
- ollama should give back the correct desktop action in correct format.


## Step 3 (flesh out before doing)

- write code which can execute these tasks

## Installation on Windows

To set up and run this project on Windows, follow these steps:

1.  **Install Python 3.11**: Ensure you have Python 3.11 installed on your system. You can download it from the official Python website. Make sure to add Python to your PATH during installation.

2.  **Install FFmpeg**: This project uses `whisper` for transcription, which may require FFmpeg for certain audio formats.
    *   Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html).
    *   Extract the downloaded archive to a directory (e.g., `C:\ffmpeg`).
    *   Add the `bin` directory of FFmpeg (e.g., `C:\ffmpeg\bin`) to your system's PATH environment variable.

3.  **Create a Virtual Environment**: It's recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    ```

4.  **Activate the Virtual Environment**:
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

5.  **Install Dependencies**: With the virtual environment activated, install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

6.  **Run the Application**:
    ```bash
    python voice_input.py
    ```
    Press and hold `Ctrl+Space` to record, release to transcribe. Press `Esc` to exit.
