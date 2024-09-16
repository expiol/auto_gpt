from tool_installer import check_and_install_tool
import logging

def handle_errors(error_message):
    if "command not found" in error_message or "not found" in error_message:
        tool_installed = check_and_install_tool(error_message)
        if tool_installed:
            logging.info("Missing tool installed successfully.")
            return True
        else:
            logging.info("Failed to install missing tool.")
            return False
    return False
