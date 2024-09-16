import platform
import subprocess
import logging

def collect_system_info():
    system_info = {}

    # Get OS information
    system_info['os'] = platform.platform()
    system_info['python_version'] = platform.python_version()
    system_info['architecture'] = platform.machine()

    # Get list of installed packages (Debian-based systems)
    try:
        result = subprocess.run(
            ['dpkg', '--get-selections'],
            capture_output=True,
            text=True,
            check=True
        )
        system_info['installed_packages'] = result.stdout
    except subprocess.CalledProcessError:
        system_info['installed_packages'] = 'Could not retrieve installed packages.'
        logging.error("Failed to retrieve installed packages.")

    # Get list of available commands
    try:
        result = subprocess.run(
            ['compgen', '-c'],
            shell=True,
            capture_output=True,
            text=True,
            executable='/bin/bash'
        )
        system_info['available_commands'] = result.stdout
    except subprocess.CalledProcessError:
        system_info['available_commands'] = 'Could not retrieve available commands.'
        logging.error("Failed to retrieve available commands.")

    return system_info
