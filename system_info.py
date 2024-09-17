import platform
import logging

def collect_system_info():
    system_info = {}

    # Get basic system information
    system_info['os'] = platform.platform()
    system_info['python_version'] = platform.python_version()
    system_info['architecture'] = platform.machine()

    # Do not collect installed packages and available commands to reduce message length

    return system_info

