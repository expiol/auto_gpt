import requests
from config import GPT_API_KEY, get_gpt_api_url
import logging
from requests.exceptions import HTTPError
from prompts import INITIALIZATION_PROMPT, COMMAND_PROMPT
from reply_filter import extract_commands_from_response

def generate_commands(task_description, system_info, model_name='gpt-4'):
    # Prepare concise system information summary
    system_info_summary = f"OS: {system_info.get('os')}\n"
    system_info_summary += f"Python Version: {system_info.get('python_version')}\n"
    system_info_summary += f"Architecture: {system_info.get('architecture')}\n"

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
    logging.debug(f"GPT response: {commands_text}")
    commands = extract_commands_from_response(commands_text)
    if not commands:
        logging.warning("No commands were extracted from GPT's response.")
        raise ValueError("No commands were extracted from GPT's response.")
    return commands

def analyze_error(error_message, previous_command, system_info, model_name='gpt-4'):
    headers = {
        'Authorization': f'Bearer {GPT_API_KEY}',
        'Content-Type': 'application/json',
    }

    # Prepare concise system information summary
    system_info_summary = f"OS: {system_info.get('os')}\n"
    system_info_summary += f"Python Version: {system_info.get('python_version')}\n"
    system_info_summary += f"Architecture: {system_info.get('architecture')}\n"

    # Construct the message
    user_message = (
        f"I ran the following command and received an error:\n\nCommand: {previous_command}\nError: {error_message}\n{system_info_summary}\n"
        "Please suggest how to fix this error by providing the exact shell commands to run, wrapped with <COMMAND> and </COMMAND> tags."
    )

    data = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that helps fix errors in shell commands. Provide only the exact shell commands needed to fix the error, wrapped with <COMMAND> and </COMMAND> tags."
            },
            {
                "role": "user",
                "content": user_message
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

def generate_summary_with_gpt(task_result, model_name='gpt-4'):
    headers = {
        'Authorization': f'Bearer {GPT_API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that summarizes technical results into human-readable form."
            },
            {
                "role": "user",
                "content": f"Please summarize the following task result: {task_result}"
            }
        ],
        "max_tokens": 200,
        "temperature": 0.5
    }

    try:
        response = requests.post(get_gpt_api_url('chat/completions'), headers=headers, json=data)
        response.raise_for_status()
    except HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise Exception(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        raise Exception(f"An error occurred: {err}")

    response_json = response.json()
    summary = response_json['choices'][0]['message']['content']
    return summary.strip()

def discuss_and_generate_commands(user_message, system_info, model_name='gpt-4'):
    headers = {
        'Authorization': f'Bearer {GPT_API_KEY}',
        'Content-Type': 'application/json',
    }

    system_info_summary = f"OS: {system_info.get('os')}\n"
    system_info_summary += f"Python Version: {system_info.get('python_version')}\n"
    system_info_summary += f"Architecture: {system_info.get('architecture')}\n"

    data = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an assistant that helps generate shell commands based on user discussions."
                )
            },
            {
                "role": "user",
                "content": (
                    f"{user_message}\n"
                    f"Here is the system information:\n{system_info_summary}\n"
                    "Please generate the shell commands needed to accomplish the task, and provide only the commands."
                )
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7
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
    logging.debug(f"GPT response: {commands_text}")
    commands = extract_commands_from_response(commands_text)
    if not commands:
        logging.warning("No commands were extracted from GPT's response.")
        return None
    return commands
