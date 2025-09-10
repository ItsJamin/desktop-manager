import requests
import json
import subprocess
import sys
import time
from voice_input import VoiceRecorder

class OllamaChat:
    def __init__(self, model="deepseek-r1:8b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.conversation_history = []
        
    def check_ollama_connection(self):
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                print(f"Connected to Ollama. Available models: {available_models}")
                
                # Check if our selected model is available
                if not any(self.model in model for model in available_models):
                    print(f"Warning: Model '{self.model}' not found. Available models: {available_models}")
                    if available_models:
                        self.model = available_models[0].split(':')[0]
                        print(f"Switching to model: {self.model}")
                
                return True
            else:
                print(f"Ollama responded with status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Cannot connect to Ollama at {self.base_url}")
            print(f"Error: {e}")
            print("Make sure Ollama is running with: ollama serve")
            return False
    
    def send_message(self, message):
        """Send a message to Ollama and get response"""
        if not message.strip():
            return "No message provided."
        
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": self.conversation_history,
                "stream": False,
                "think": False
            }
            
            print(f"Sending to Ollama: {message}")
            print("Waiting for response...")
            
            # Send request to Ollama
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result.get('message', {}).get('content', 'No response received')
                
                # Add assistant response to conversation history
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                print(f"\nOllama Response:\n{assistant_message}\n")
                return assistant_message
            else:
                error_msg = f"Error: Ollama returned status code {response.status_code}"
                print(error_msg)
                return error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Request timed out. The model might be taking too long to respond."
            print(error_msg)
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            print(error_msg)
            return error_msg
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse response: {e}"
            print(error_msg)
            return error_msg
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
        print("Conversation history cleared.")

class VoiceToOllamaChat:
    def __init__(self, model="deepseek-r1:8b", base_url="http://localhost:11434"):
        self.ollama_chat = OllamaChat(model, base_url)
        self.voice_recorder = VoiceRecorder()
        
        # Override the voice recorder's transcription method to send to Ollama
        self.original_transcribe = self.voice_recorder.stop_recording_and_transcribe
        self.voice_recorder.stop_recording_and_transcribe = self.transcribe_and_send_to_ollama
    
    def transcribe_and_send_to_ollama(self):
        """Override method to capture transcription and send to Ollama"""
        if not self.voice_recorder.recording:
            return

        print("Recording stopped. Transcribing...")
        self.voice_recorder.recording = False

        # Stop and close the audio stream safely
        if self.voice_recorder.stream:
            self.voice_recorder.stream.stop()
            self.voice_recorder.stream.close()
            self.voice_recorder.stream = None

        if not self.voice_recorder.audio_data:
            print("No audio recorded.")
            return

        # Concatenate recorded blocks
        import numpy as np
        recorded_audio = np.concatenate(self.voice_recorder.audio_data, axis=0)

        # Convert to mono if necessary
        if recorded_audio.ndim > 1:
            recorded_audio = recorded_audio.mean(axis=1)

        # Convert to float32 in range [-1, 1]
        recorded_audio = recorded_audio.astype(np.float32)
        max_val = np.max(np.abs(recorded_audio))
        if max_val > 0:
            recorded_audio /= max_val

        try:
            if self.voice_recorder.model is None:
                print("Loading Whisper model (this may take a moment)...")
                import tempfile
                import os
                import whisper
                model_cache_dir = os.path.join(tempfile.gettempdir(), "whisper_models")
                os.makedirs(model_cache_dir, exist_ok=True)
                self.voice_recorder.model = whisper.load_model("base", download_root=model_cache_dir)

            # Transcribe directly from NumPy array
            result = self.voice_recorder.model.transcribe(
                audio=recorded_audio,
                fp16=False
            )
            transcribed_text = result['text'].strip()
            print(f"You said: {transcribed_text}")
            
            # Send transcribed text to Ollama if it's not empty
            if transcribed_text:
                self.ollama_chat.send_message(transcribed_text)
            else:
                print("No speech detected.")
                
        except Exception as e:
            print(f"Error during transcription: {e}")
    
    def run(self):
        """Run the voice-to-Ollama chat system"""
        print("=== Voice to Ollama Chat ===")
        
        # Check Ollama connection first
        if not self.ollama_chat.check_ollama_connection():
            print("Cannot proceed without Ollama connection.")
            return
        
        print(f"\nUsing model: {self.ollama_chat.model}")
        print(f"Press and hold '{self.voice_recorder.hotkey}' to record your voice message")
        print("Release the key to transcribe and send to Ollama")
        print("Press 'c' to clear conversation history")
        print("Press 'esc' to exit")
        print("-" * 50)
        
        import keyboard
        
        while True:
            if keyboard.is_pressed('esc'):
                print("Exiting program.")
                break
            
            if keyboard.is_pressed('c'):
                self.ollama_chat.clear_conversation()
                time.sleep(0.5)  # Prevent multiple clears
                continue

            if keyboard.is_pressed(self.voice_recorder.hotkey):
                if not self.voice_recorder.recording:
                    self.voice_recorder.start_recording()
            else:
                if self.voice_recorder.recording:
                    self.transcribe_and_send_to_ollama()
            
            time.sleep(0.05)  # Small delay to prevent high CPU usage

def main():
    """Main function with command line argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice to Ollama Chat")
    parser.add_argument("--model", default="deepseek-r1:8b", help="Ollama model to use (default: deepseek-r1:8b)")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama base URL (default: http://localhost:11434)")
    parser.add_argument("--text-only", action="store_true", help="Run in text-only mode without voice input")
    parser.add_argument("--think=false")

    args = parser.parse_args()
    
    if args.text_only:
        # Text-only mode
        chat = OllamaChat(args.model, args.url)
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
    else:
        # Voice mode
        voice_chat = VoiceToOllamaChat(args.model, args.url)
        voice_chat.run()

if __name__ == "__main__":
    main()
