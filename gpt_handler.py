import requests
from config import GPT_API_KEY, get_gpt_api_url
import logging
from requests.exceptions import HTTPError
from prompts import INITIALIZATION_PROMPT, COMMAND_PROMPT
from reply_filter import extract_commands_from_response  # Import the reply filter

def generate_commands(task_description, system_info, model_name='gpt-4'):
    # Prepare system information summary
    system_info_summary = f"OS: {system_info.get('os')}\n"
    system_info_summary += f"Python Version: {system_info.get('python_version')}\n"
    system_info_summary += f"Architecture: {system_info.get('architecture')}\n"

    # Limit the length to avoid exceeding token limits
    installed_packages = '\n'.join(system_info.get('installed_packages', '').split('\n')[:50])
    available_commands = '\n'.join(system_info.get('available_commands', '').split('\n')[:50])

    headers = {
        'Authorization': f'Bearer {GPT_API_KEY}',
        'Content-Type': 'application/json',
    }

    # Format the command prompt with the task description
    command_prompt = COMMAND_PROMPT.format(task_description=task_description)

    data = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"{INITIALIZATION_PROMPT}\n"
                    "Here is the system information to help you generate compatible commands:\n\n"
                    f"{system_info_summary}\n"
                    f"Installed Packages:\n{installed_packages}\n\n"
                    f"Available Commands:\n{available_commands}\n\n"
                    "Based on this system, generate the commands needed."
                )
            },
            {
                "role": "user",
                "content": command_prompt
            }
        ],
        "max_tokens": 1000,
        "temperature": 0
    }

    try:
        response = requests.post(get_gpt_api_url('chat/completions'), headers=headers, json=data)
        response.raise_for_status()
    except HTTPError as http_err:
        error_content = response.json()
        logging.error(f"HTTP error occurred: {http_err} - {error_content}")
        raise Exception(f"HTTP error occurred: {http_err} - {error_content}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        raise Exception(f"An error occurred: {err}")

    response_json = response.json()

    commands_text = response_json['choices'][0]['message']['content']
    commands = extract_commands_from_response(commands_text)
    if not commands:
        raise ValueError("No commands were extracted from GPT's response.")
    return commands

def analyze_error(error_message, previous_command, model_name='gpt-4'):
    headers = {
        'Authorization': f'Bearer {GPT_API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that helps fix errors in shell commands. Provide only the exact shell commands needed to fix the error, wrapped with <COMMAND> and </COMMAND> tags."
            },
            {
                "role": "user",
                "content": (
                    f"I ran the following command and received an error:\n\nCommand: {previous_command}\nError: {error_message}\n\n"
                    "Please suggest how to fix this error by providing the exact shell commands to run, wrapped with <COMMAND> and </COMMAND> tags."
                )
            }
        ],
        "max_tokens": 150,
        "temperature": 0
    }

    try:
        response = requests.post(get_gpt_api_url('chat/completions'), headers=headers, json=data)
        response.raise_for_status()
    except HTTPError as http_err:
        error_content = response.json()
        logging.error(f"HTTP error occurred: {http_err} - {error_content}")
        raise Exception(f"HTTP error occurred: {http_err} - {error_content}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        raise Exception(f"An error occurred: {err}")

    response_json = response.json()

    suggestion = response_json['choices'][0]['message']['content']
    return suggestion.strip()
