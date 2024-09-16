import subprocess
import re
import logging

def check_and_install_tool(error_message):
    if "command not found" in error_message or "not found" in error_message:
        # Extract the tool name from the error message
        tool_name = extract_tool_name(error_message)
        if not tool_name:
            logging.info("Could not determine the missing tool name from the error message.")
            return False

        try:
            # Update package lists (suppress output)
            subprocess.run(
                ["apt-get", "update", "-qq"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
            )

            # Install the missing tool (suppress output)
            subprocess.run(
                ["apt-get", "install", "-y", tool_name, "-qq"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            logging.info(f"Installed missing tool: {tool_name}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install {tool_name}: {e}")
            return False
    return False

def extract_tool_name(error_message):
    # Patterns to match the tool name in different error messages
    patterns = [
        r"bash: (\S+): command not found",
        r": (\S+): command not found",
        r": (\S+): not found",
        r"(\S+): command not found"
    ]
    for pattern in patterns:
        match = re.search(pattern, error_message)
        if match:
            return match.group(1)
    return None
