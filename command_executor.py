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

def execute_command(command, suppress_output=False, timeout=60):
    logging.debug(f"Executing command: {command}")
    if not is_command_safe(command):
        logging.warning(f"Command is deemed unsafe and was not executed: {command}")
        return False, "Command is deemed unsafe and was not executed."

    try:
        # Use shlex to safely split the command
        args = shlex.split(command)
        if suppress_output:
            result = subprocess.run(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                timeout=timeout
            )
            return True, result.stderr  # Return stderr in case there are important messages
        else:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            return True, result.stdout
    except subprocess.TimeoutExpired:
        logging.error(f"Command timed out after {timeout} seconds: {command}")
        return False, f"Command timed out after {timeout} seconds."
    except subprocess.CalledProcessError as e:
        logging.error(f"Command execution failed: {e}")
        return False, e.stderr
    except Exception as e:
        logging.exception("An error occurred while executing the command")
        return False, str(e)

