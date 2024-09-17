from tool_installer import check_and_install_tool
import logging

def handle_errors(error_message, current_command=None):
    logging.debug(f"Handling error: {error_message}")
    if "command not found" in error_message or "not found" in error_message:
        tool_installed = check_and_install_tool(error_message)
        if tool_installed:
            logging.info("Missing tool installed successfully.")
            return True
        else:
            logging.warning("Failed to install missing tool.")
            return False
    elif "permission denied" in error_message.lower():
        if current_command and not current_command.startswith('sudo '):
            # Modify the command to add sudo
            modified_command = 'sudo ' + current_command
            logging.info("Added sudo to the command to resolve permission issues.")
            return modified_command
        else:
            logging.warning("Permission denied error, but command already has sudo or no command provided.")
            return False
    else:
        logging.info("Error type not handled by handle_errors.")
    return False

