import subprocess
import json
import webbrowser
import os

class TaskExecutor:
    def execute_commands(self, json_commands):
        """
        Executes a list of commands provided in JSON format.
        """
        try:
            commands = json.loads(json_commands)
            if not isinstance(commands, list):
                print("Error: Expected a JSON array of commands.")
                return

            for command_obj in commands:
                command_type = command_obj.get("command_type")
                parameters = command_obj.get("parameters", {})

                if command_type == "open_terminal_and_execute":
                    self._open_terminal_and_execute(parameters)
                elif command_type == "open_application":
                    self._open_application(parameters)
                elif command_type == "open_url":
                    self._open_url(parameters)
                else:
                    print(f"Unknown command type: {command_type}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON commands: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during command execution: {e}")

    def _open_terminal_and_execute(self, parameters):
        command = parameters.get("command")
        if not command:
            print("Error: 'command' parameter is missing for open_terminal_and_execute.")
            return

        print(f"Executing in terminal: {command}")
        try:
            # For Windows, we can use 'start cmd /k' to open a new terminal and keep it open
            # For Linux/macOS, a simple subprocess.Popen might suffice, but it depends on the terminal emulator
            if os.name == 'nt': # Windows
                subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
            else: # Linux/macOS
                # This might need adjustment based on the user's default terminal
                # For example, 'gnome-terminal -e' or 'xterm -e' for Linux, 'open -a Terminal' for macOS
                # For simplicity, we'll just run the command directly, which might not open a new visible terminal
                subprocess.Popen(command, shell=True)
        except Exception as e:
            print(f"Failed to open terminal and execute command: {e}")

    def _open_application(self, parameters):
        application_name = parameters.get("application_name")
        if not application_name:
            print("Error: 'application_name' parameter is missing for open_application.")
            return

        print(f"Opening application: {application_name}")
        try:
            if os.name == 'nt': # Windows
                os.startfile(application_name)
            else: # Linux/macOS
                subprocess.Popen(['open', application_name]) # 'open' command for macOS, might need 'xdg-open' for Linux
        except Exception as e:
            print(f"Failed to open application {application_name}: {e}")

    def _open_url(self, parameters):
        url = parameters.get("url")
        if not url:
            print("Error: 'url' parameter is missing for open_url.")
            return

        print(f"Opening URL: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open URL {url}: {e}")

if __name__ == "__main__":
    executor = TaskExecutor()
    
    # Example usage:
    example_commands = """
    [
      {
        "command_type": "open_terminal_and_execute",
        "parameters": {
          "command": "echo Hello from terminal!"
        }
      },
      {
        "command_type": "open_application",
        "parameters": {
          "application_name": "notepad"
        }
      },
      {
        "command_type": "open_url",
        "parameters": {
          "url": "https://www.google.com"
        }
      }
    ]
    """
    print("Executing example commands...")
    executor.execute_commands(example_commands)
