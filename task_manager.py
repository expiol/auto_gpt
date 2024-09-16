import logging
import re  # Ensure re is imported at the top
from gpt_handler import generate_commands, analyze_error
from command_executor import execute_command
from system_info import collect_system_info
from reply_filter import extract_commands_from_response  # Import the reply filter

class TaskManager:
    def __init__(self):
        self.commands = []
        self.current_command_index = 0
        self.task_complete = False
        self.task_result = ""  # Output from main task commands
        self.model_name = 'gpt-4'  # Default to gpt-4
        self.error_handling_output = ""  # Output from error handling processes

    def initialize_task(self, task_description, model_name='gpt-4'):
        try:
            self.model_name = model_name
            # Collect system information
            system_info = collect_system_info()
            # Generate commands with system information
            self.commands = generate_commands(task_description, system_info, self.model_name)
            self.current_command_index = 0
            self.task_complete = False
            self.task_result = ""
            self.error_handling_output = ""
        except Exception as e:
            logging.exception("Error in initialize_task")
            raise e

    def execute_next_command(self):
        if self.current_command_index < len(self.commands):
            command = self.commands[self.current_command_index]
            # Check if the command is an installation command
            if self.is_installation_command(command):
                # Execute installation command with suppressed output
                success, output = execute_command(command, suppress_output=True)
                if success:
                    logging.info(f"Installation command executed successfully: {command}")
                else:
                    logging.error(f"Failed to execute installation command: {command}")
            else:
                # Execute regular command
                success, output = execute_command(command)
                if success:
                    self.task_result += output  # Only accumulate outputs from main commands
                else:
                    # Do not increment current_command_index so that we can retry the command after handling errors
                    return False, output

            self.current_command_index += 1
            return True, output
        else:
            self.task_complete = True
            return True, "Task completed"

    def is_task_complete(self):
        return self.task_complete

    def is_installation_command(self, command):
        # Method to detect installation or update commands
        pattern = r'^\s*(sudo\s+)?(apt(-get)?|aptitude|yum|dnf|pacman|zypper|brew|pip3?)\s+(install|update|upgrade)\b'
        return re.match(pattern, command.strip()) is not None

    def analyze_error_with_gpt(self, error_message):
        previous_command = self.commands[self.current_command_index]
        suggestion = analyze_error(error_message, previous_command, self.model_name)
        return suggestion

    def apply_suggestion(self, suggestion):
        # Use the reply filter to extract commands from the suggestion
        commands = extract_commands_from_response(suggestion)
        if not commands:
            logging.info("No commands extracted from GPT's suggestion.")
            return False
        # Execute the commands (usually installation commands)
        for cmd in commands:
            success, output = execute_command(cmd, suppress_output=True)  # Suppress output here
            if success:
                logging.info(f"Suggested command executed successfully: {cmd}")
            else:
                logging.info(f"Failed to execute suggested command: {cmd}")
                return False
        return True

    def get_task_result(self):
        return self.task_result  # Only return outputs from main commands

    def get_current_command(self):
        if self.current_command_index < len(self.commands):
            return self.commands[self.current_command_index]
        else:
            return None
