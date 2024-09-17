# Auto-Pentest

Auto-Pentest is an automated penetration testing tool that uses OpenAI's GPT model to analyze system information and generate appropriate shell commands to complete tasks. The tool helps with penetration testing and tool installation by analyzing error logs and suggesting fixes.

## Features

- Generates commands required for penetration testing through the GPT model (GPT-4 by default).

- Automatically handles common errors and attempts to fix them, such as automatically installing missing tools when the command is not found.

- Generates system information to ensure that the command is compatible with the current system.

- Supports providing task execution functions through the Flask API.

## Project structure

```bash
auto-pentest/
├── app.py # Flask application entry
├── command_executor.py # Command execution module
├── config.py # Configuration file, manage GPT API related configuration
├── docker-compose.yml # Docker Compose configuration file
├── Dockerfile # Docker image configuration file
├── error_handler.py # Error handling module
├── gpt_handler.py # Module for processing GPT requests
├── prompts.py # Define prompt words for GPT
├── requirements.txt # Project dependency file
├── system_info.py # System information collection module
├── task_manager.py # Core logic for managing task execution
├── tests/ # Test module
│ ├── test_app.py # Test Flask API
│ ├── test_command_executor.py # Test command execution
│ ├── test_gpt_handler.py # Test GPT module
│ ├── test_task_manager.py # Test task manager
├── logs/ # Directory for storing logs
```

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/expiol/auto_gpt.git
cd auto-pentest
```

### 2. Set environment variables


Export your API key with export OPENAI_API_KEY='<your key here>',export API base with export OPENAI_BASEURL='https://api.xxxx.xxx/v1' ,if you need.
Or you can use this command to modify
```bash
nano .env
```

### 3. Run with Docker

You can run the project with Docker:

```bash
docker-compose up
```
### 4. Run with python3(recommend)

You can run the project with command:

```bash
python3 app.py
```

This will start the service and run it on port `8080` Run on .

### 5. Run the API

The API provides a simple endpoint to execute tasks. You can use `curl` or Postman to test:

```bash
curl -X POST http://localhost:8080/execute-task \
-H "Content-Type: application/json" \
-d '{
"task_description": "echo Hello, World!",
"model_name": "gpt-4"
}'
```

## File Description

* `app.py`: Flask application that provides the `/execute-task` endpoint for users to submit task descriptions and execute tasks.

* `command_executor.py`: Handles the execution of shell commands.
* `config.py`: Load OpenAI's API Key and other related configuration information.
* `gpt_handler.py`: Interact with the GPT API to generate penetration test commands or handle errors.
* `task_manager.py`: Manage task execution and error handling, including generating commands and analyzing errors.
* `error_handler.py`: Handle common errors, such as command not found, and automatically install missing tools.
* `prompts.py`: Contains prompts for interacting with GPT.
* `system_info.py`: Collect information about the current system, such as operating system version, installed packages, etc.

## Dependencies

You can install dependencies through the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

The project mainly depends on the following libraries:

* Flask
* Requests
* Python-dotenv

## Usage Notes

* When using this tool, make sure you have a full understanding of the generated commands to avoid unexpected operations that affect system security.
* This project uses OpenAI's GPT model to generate commands. Make sure your API Key has enough quota and permissions to call related models (such as GPT-4).

## Contribution

If you want to contribute code or make suggestions, please create a Pull Request or submit an Issue.

## License

This project is based on the Apache-2.0 license. Please refer to the LICENSE file for details.

