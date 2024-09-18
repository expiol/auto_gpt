from flask import Flask, request, jsonify
from task_manager import TaskManager
import logging
from logging_config import setup_logging
import json  # Import json to format the response

app = Flask(__name__)
setup_logging()
task_manager = TaskManager()

@app.before_request
def log_request_info():
    app.logger.info(f"Received {request.method} request at {request.path} with data: {request.get_json()}")

@app.after_request
def log_response_info(response):
    app.logger.info(f"Responded with status {response.status_code} and data: {response.get_data(as_text=True)}")
    return response

@app.route('/execute-task', methods=['POST'])
def execute_task():
    try:
        data = request.get_json()
        task_description = data.get('task_description')
        model_name = data.get('model_name', 'gpt-4')  # Default to gpt-4

        if not task_description:
            return jsonify({'status': 'error', 'message': 'Task description is required.'}), 400

        # Initialize task with the selected model
        task_manager.initialize_task(task_description, model_name)

        # Execute commands until completion
        while not task_manager.is_task_complete():
            success, output = task_manager.execute_next_command()

            if not success:
                # Handle errors
                continue

        # Summarize task result with GPT
        summarized_result = task_manager.summarize_task_result_with_gpt()

        # Replace '\n' with actual newlines in the result for better readability
        formatted_summary = summarized_result.replace("\\n", "\n")

        # Return the formatted summary with actual newlines
        return jsonify({'status': 'success', 'summary': formatted_summary}), 200

    except Exception as e:
        app.logger.exception("An error occurred in /execute-task")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

