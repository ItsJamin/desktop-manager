import keyboard
import time
from ollama_chat import OllamaChat
from voice_input import VoiceRecorder
from task_executor import TaskExecutor
import json

class MainApp:
    def __init__(self):
        self.ollama_chat = OllamaChat()
        self.voice_recorder = VoiceRecorder()
        self.task_executor = TaskExecutor()
        self.hotkey = "ctrl+space" # Define hotkey here or load from .env

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
                    print("Recording stopped. Transcribing...")
                    transcribed_text = self.voice_recorder.stop_recording()
                    
                    if transcribed_text:
                        print(f"You said: {transcribed_text}")
                        ollama_response = self.ollama_chat.send_message(transcribed_text)
                        
                        if ollama_response:
                            try:
                                # Attempt to parse Ollama's response as JSON commands
                                self.task_executor.execute_commands(ollama_response)
                            except json.JSONDecodeError:
                                print("Ollama did not return valid JSON commands. Displaying raw response:")
                                print(ollama_response)
                        else:
                            print("No response from Ollama.")
                    else:
                        print("No speech detected.")
            
            time.sleep(0.05)  # Small delay to prevent high CPU usage

def main():
    app = MainApp()
    app.run_voice_chat()

if __name__ == "__main__":
    main()
