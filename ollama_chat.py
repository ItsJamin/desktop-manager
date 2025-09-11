import requests
import json
import os
from dotenv import load_dotenv

class OllamaChat:
    def __init__(self):
        load_dotenv()
        self.model = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.conversation_history = []
        self._set_system_prompt()
        
    def _set_system_prompt(self):
        system_prompt = """
You are a desktop manager assistant on Windows. Your task is to translate user requests into a list of structured JSON commands.
You MUST respond ONLY with a JSON array of command objects. Do NOT include any other text or explanations.

Each command object must have a "command_type" and a "parameters" object.

Available command types and their parameters:

1.  "open_terminal_and_execute":
    *   Description: Opens a terminal and executes a specified command.
    *   Parameters:
        *   "command" (string, required): The shell command to execute.

2.  "open_application":
    *   Description: Opens a specified application.
    *   Parameters:
        *   "application_name" (string, required): The name of the application to open (e.g., "notepad", "chrome", "vscode").

3.  "open_url":
    *   Description: Opens a specified URL in the default web browser.
    *   Parameters:
        *   "url" (string, required): The URL to open (e.g., "https://google.com").

Example of expected JSON output:
[
  {
    "command_type": "open_terminal_and_execute",
    "parameters": {
      "command": "ls -l"
    }
  },
  {
    "command_type": "open_application",
    "parameters": {
      "application_name": "notepad"
    }
  }
]

Give nothing else BUT the JSON array of commands. Ensure the JSON is properly formatted.
"""
        self.conversation_history.append({"role": "system", "content": system_prompt})

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
        self._set_system_prompt()
        print("Conversation history cleared.")

if __name__ == "__main__":
    chat = OllamaChat()
    if not chat.check_ollama_connection():
        exit()
    
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
