import keyboard
import whisper
import tempfile
import os
import time
from ollama_chat import OllamaChat
from voice_input import VoiceRecorder

class MainApp:
    def __init__(self):
        self.ollama_chat = OllamaChat()
        self.voice_recorder = VoiceRecorder()
        self.whisper_model = None
        self.hotkey = "ctrl+space" # Define hotkey here or load from .env

    def _load_whisper_model(self):
        if self.whisper_model is None:
            print("Loading Whisper model (this may take a moment)...")
            model_cache_dir = os.path.join(tempfile.gettempdir(), "whisper_models")
            os.makedirs(model_cache_dir, exist_ok=True)
            self.whisper_model = whisper.load_model("base", download_root=model_cache_dir)

    def transcribe_audio(self, audio_data):
        """Transcribe audio data using Whisper."""
        if audio_data is None:
            return ""

        self._load_whisper_model()
        
        try:
            result = self.whisper_model.transcribe(
                audio=audio_data,
                fp16=False
            )
            return result['text'].strip()
        except Exception as e:
            print(f"Error during transcription: {e}")
            return ""

    def run_voice_chat(self):
        """Run the voice-to-Ollama chat system"""
        print("=== Voice to Ollama Chat ===")
        
        # Check Ollama connection first
        if not self.ollama_chat.check_ollama_connection():
            print("Cannot proceed without Ollama connection.")
            return
        
        print(f"\nUsing model: {self.ollama_chat.model}")
        print(f"Press and hold '{self.hotkey}' to record your voice message")
        print("Release the key to transcribe and send to Ollama")
        print("Press 'c' to clear conversation history")
        print("Press 'esc' to exit")
        print("-" * 50)
        
        while True:
            if keyboard.is_pressed('esc'):
                print("Exiting program.")
                break
            
            if keyboard.is_pressed('c'):
                self.ollama_chat.clear_conversation()
                time.sleep(0.5)  # Prevent multiple clears
                continue

            if keyboard.is_pressed(self.hotkey):
                if not self.voice_recorder.recording:
                    self.voice_recorder.start_recording()
            else:
                if self.voice_recorder.recording:
                    recorded_audio = self.voice_recorder.stop_recording()
                    if recorded_audio is not None:
                        print("Recording stopped. Transcribing...")
                        transcribed_text = self.transcribe_audio(recorded_audio)
                        print(f"You said: {transcribed_text}")
                        
                        if transcribed_text:
                            self.ollama_chat.send_message(transcribed_text)
                        else:
                            print("No speech detected.")
            
            time.sleep(0.05)  # Small delay to prevent high CPU usage

    def run_text_chat(self):
        """Run the text-only chat system"""
        chat = self.ollama_chat
        if not chat.check_ollama_connection():
            return
        
        print(f"=== Text Chat with Ollama ({chat.model}) ===")
        print("Type your messages (press Enter to send)")
        print("Type 'clear' to clear conversation history")
        print("Type 'quit' or 'exit' to quit")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['quit', 'exit']:
                    break
                elif user_input.lower() == 'clear':
                    chat.clear_conversation()
                    continue
                elif user_input:
                    chat.send_message(user_input)
            except KeyboardInterrupt:
                print("\nExiting...")
                break

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice to Ollama Chat")
    parser.add_argument("--text-only", action="store_true", help="Run in text-only mode without voice input")

    args = parser.parse_args()
    
    app = MainApp()

    if args.text_only:
        app.run_text_chat()
    else:
        app.run_voice_chat()

if __name__ == "__main__":
    main()
