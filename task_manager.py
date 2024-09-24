import logging
import re
import threading
from gpt_handler import (
    generate_commands,
    analyze_error,
    generate_summary_with_gpt,
    discuss_and_generate_commands,
)
from command_executor import execute_command_with_real_time_output
from system_info import collect_system_info
from reply_filter import extract_commands_from_response
from error_handler import handle_errors
from socketio_instance import socketio

class TaskManager:
    def __init__(self):
        self.commands = []
        self.current_command_index = 0
        self.task_complete = False
        self.task_result = ""
        self.model_name = 'gpt-4'
        self.paused = threading.Event()
        self.paused.set()  # Initially not paused
        self.skip_current = False
        self.current_process = None
        self.current_process_lock = threading.Lock()
        logging.info("TaskManager initialized")

    def initialize_task(self, task_description, model_name='gpt-4'):
        try:
            self.model_name = model_name
            logging.info(f"Initializing task with description: {task_description} and model: {model_name}")
            system_info = collect_system_info()
            logging.info(f"Collected system information: {system_info}")
            self.commands = generate_commands(task_description, system_info, self.model_name)
            logging.info(f"Generated commands: {self.commands}")
            self.current_command_index = 0
            self.task_complete = False
            self.task_result = ""
        except Exception as e:
            logging.exception("Error in initialize_task")
            raise e

    def get_command_list(self):
        return self.commands

    def set_command_list(self, new_commands):
        self.commands = new_commands
        logging.info(f"Command list updated: {self.commands}")

    def pause(self):
        self.paused.clear()
        logging.info("Task paused")

    def resume(self):
        self.paused.set()
        logging.info("Task resumed")

    def skip(self):
        self.skip_current = True
        logging.info("当前命令将被跳过")
        with self.current_process_lock:
            if self.current_process and self.current_process.poll() is None:
                logging.info("正在终止当前命令执行")
                self.current_process.terminate()
                self.current_process = None

    def execute_next_command(self):
        self.paused.wait()  # Wait if paused

        if self.current_command_index < len(self.commands):
            command = self.commands[self.current_command_index]
            logging.info(f"Executing command {self.current_command_index + 1}/{len(self.commands)}: {command}")

            # Emit the current command to clients
            socketio.emit('command_output', {'command': command, 'output': f"Starting command: {command}"})

            max_retries = 3
            retries = 0

            while retries < max_retries:
                self.paused.wait()  # Check pause status

                # Check if need to skip current command
                if self.skip_current:
                    logging.info(f"Skipping current command: {command}")
                    self.skip_current = False
                    self.current_command_index += 1
                    return True, f"Skipped command: {command}"

                # Execute command with real-time output
                success, output = self.execute_command_with_real_time_output(command)

                if success:
                    if not self.is_installation_command(command):
                        self.task_result += output
                    logging.info(f"Command executed successfully: {command}")
                    self.current_command_index += 1
                    return True, output
                else:
                    logging.error(f"Failed to execute command: {command}")
                    retries += 1
                    logging.info(f"Retrying command ({retries}/{max_retries}): {command}")

                    # Handle errors
                    error_handled = self.handle_errors(output)
                    if error_handled:
                        continue
                    else:
                        break

            # Exceeded max retries, skip command
            logging.error(f"Command failed after {max_retries} retries: {command}")
            self.current_command_index += 1
            return False, output
        else:
            self.task_complete = True
            logging.info("All commands executed, task completed")
            return True, "Task completed"

    def execute_command_with_real_time_output(self, command):
        try:
            process = execute_command_with_real_time_output(command)

            if process is None:
                return False, "Failed to start the command."

            output_lines = []
            with self.current_process_lock:
                self.current_process = process

            # Read real-time output
            for line in iter(process.stdout.readline, ''):
                if line == '' and process.poll() is not None:
                    break
                output_lines.append(line)
                # Emit each line to clients
                socketio.emit('command_output', {'command': command, 'output': line})

            process.wait()
            returncode = process.returncode

            with self.current_process_lock:
                self.current_process = None

            output = ''.join(output_lines)
            success = returncode == 0

            return success, output

        except Exception as e:
            logging.exception("Error while executing command")
            return False, str(e)

    def is_task_complete(self):
        logging.info(f"Task complete status: {self.task_complete}")
        return self.task_complete

    def is_installation_command(self, command):
        pattern = r'^\s*(sudo\s+)?(apt(-get)?|aptitude|yum|dnf|pacman|zypper|brew|pip3?)\s+(install|update|upgrade)\b'
        is_install = re.match(pattern, command.strip()) is not None
        logging.info(f"Command '{command}' is installation command: {is_install}")
        return is_install

    def analyze_error_with_gpt(self, error_message):
        try:
            previous_command = self.commands[self.current_command_index]
            logging.info(f"Analyzing error with GPT for command: {previous_command}")
            system_info = collect_system_info()
            suggestion = analyze_error(error_message, previous_command, system_info, self.model_name)
            logging.info(f"Error analyzed with GPT. Suggestion: {suggestion}")
            return suggestion
        except Exception as e:
            logging.exception("Error in analyze_error_with_gpt")
            return None

    def apply_suggestion(self, suggestion):
        if not suggestion or not isinstance(suggestion, str):
            logging.warning("No valid suggestion to apply.")
            return False
        commands = extract_commands_from_response(suggestion)
        if not commands:
            logging.info("No commands extracted from GPT's suggestion.")
            return False
        for cmd in commands:
            logging.info(f"Executing suggested command: {cmd}")
            success, output = self.execute_command_with_real_time_output(cmd)
            # Emit the output to clients
            socketio.emit('command_output', {'command': cmd, 'output': output})

            if success:
                logging.info(f"Suggested command executed successfully: {cmd}")
            else:
                logging.error(f"Failed to execute suggested command: {cmd}")
                return False
        return True

    def get_task_result(self):
        logging.info(f"Task result: {self.task_result}")
        return self.task_result

    def summarize_task_result_with_gpt(self):
        try:
            logging.info("Summarizing task result using GPT")
            system_info = collect_system_info()
            prompt = f"Summarize the following task result:\n{self.task_result}\nSystem info: {system_info}"
            summary = generate_summary_with_gpt(prompt, self.model_name)
            logging.info(f"Summary generated: {summary}")
            return summary
        except Exception as e:
            logging.exception("Error in summarize_task_result_with_gpt")
            return self.task_result

    def get_current_command(self):
        if self.current_command_index < len(self.commands):
            current_command = self.commands[self.current_command_index]
            logging.info(f"Current command: {current_command}")
            return current_command
        else:
            logging.info("No current command, all commands executed")
            return None

    def handle_errors(self, error_message):
        current_command = self.get_current_command()
        return handle_errors(error_message, current_command)

    def discuss_with_gpt(self, user_message):
        try:
            logging.info(f"User message for discussion: {user_message}")
            # Use GPT to discuss and generate new commands
            system_info = collect_system_info()
            new_commands = discuss_and_generate_commands(user_message, system_info, self.model_name)
            logging.info(f"New commands generated from discussion: {new_commands}")
            if new_commands:
                self.commands = new_commands
                self.current_command_index = 0  # Reset command index
                return {'commands': new_commands}
            else:
                return "No new commands were generated."
        except Exception as e:
            logging.exception("Error in discuss_with_gpt")
            return "An error occurred during the discussion with GPT."
