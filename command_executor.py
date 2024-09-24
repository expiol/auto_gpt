import subprocess
import shlex
import re
import logging

def is_command_safe(command):
    """
    Checks if the command is safe to execute.
    """
    # List of disallowed commands or patterns
    disallowed_patterns = [
        r'rm\s+-rf\s+/',          # Prevents recursive deletion of root directory
        r':\s*>',                 # Prevents overwriting critical files
        r'(^|\s)shutdown(\s|$)',  # Prevents shutdown commands
        r'(^|\s)reboot(\s|$)',    # Prevents reboot commands
        r'(^|\s)init\s+0(\s|$)',  # Prevents system halt
        # Add more patterns as needed
    ]
    for pattern in disallowed_patterns:
        if re.search(pattern, command):
            return False
    return True

def execute_command_with_real_time_output(command):
    logging.debug(f"Executing command: {command}")
    if not is_command_safe(command):
        logging.warning(f"Command is deemed unsafe and was not executed: {command}")
        return None

    try:
        args = shlex.split(command)
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        return process
    except Exception as e:
        logging.exception("An error occurred while executing the command")
        return None
