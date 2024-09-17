import subprocess
import re
import logging
import shutil

def check_and_install_tool(error_message):
    if "command not found" in error_message or "not found" in error_message:
        # Extract the tool name from the error message
        tool_name = extract_tool_name(error_message)
        if not tool_name:
            logging.info("Could not determine the missing tool name from the error message.")
            return False

        # Detect available package manager
        package_manager = detect_package_manager()
        if not package_manager:
            logging.error("No supported package manager found.")
            return False

        try:
            # Update package lists
            update_command = get_update_command(package_manager)
            subprocess.run(update_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            # Install the missing tool
            install_command = get_install_command(package_manager, tool_name)
            subprocess.run(install_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            logging.info(f"Installed missing tool: {tool_name}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install {tool_name} using {package_manager}: {e}")
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

def detect_package_manager():
    package_managers = ['apt-get', 'yum', 'dnf', 'pacman', 'zypper', 'brew']
    for pm in package_managers:
        if shutil.which(pm):
            return pm
    return None

def get_update_command(package_manager):
    commands = {
        'apt-get': ['apt-get', 'update', '-qq'],
        'yum': ['yum', 'makecache'],
        'dnf': ['dnf', 'makecache'],
        'pacman': ['pacman', '-Sy'],
        'zypper': ['zypper', 'refresh'],
        'brew': ['brew', 'update']
    }
    return commands.get(package_manager, [])

def get_install_command(package_manager, tool_name):
    commands = {
        'apt-get': ['apt-get', 'install', '-y', tool_name, '-qq'],
        'yum': ['yum', 'install', '-y', tool_name],
        'dnf': ['dnf', 'install', '-y', tool_name],
        'pacman': ['pacman', '-S', '--noconfirm', tool_name],
        'zypper': ['zypper', 'install', '-y', tool_name],
        'brew': ['brew', 'install', tool_name]
    }
    return commands.get(package_manager, [])

