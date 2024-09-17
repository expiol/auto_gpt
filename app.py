from flask import Flask, request, jsonify
from task_manager import TaskManager
import logging
from logging_config import setup_logging

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
                # Handle errors, including tool installation
                error_handled = task_manager.handle_errors(output)
                if error_handled is True:
                    app.logger.info("Error handled successfully. Retrying command.")
                    continue  # Retry the current command
                elif isinstance(error_handled, str):
                    # Command modified (e.g., added sudo)
                    task_manager.commands[task_manager.current_command_index] = error_handled
                    app.logger.info(f"Modified command to resolve error: {error_handled}")
                    continue  # Retry with modified command
                else:
                    # Use GPT to analyze the error and suggest fixes
                    suggestion = task_manager.analyze_error_with_gpt(output)
                    if suggestion:
                        # Try to apply the suggestion
                        applied = task_manager.apply_suggestion(suggestion)
                        if applied:
                            app.logger.info("Applied suggestion from GPT. Retrying command.")
                            continue
                        else:
                            app.logger.warning("Failed to apply suggestion from GPT.")
                    else:
                        app.logger.warning("No suggestion provided by GPT.")
                    # Decide whether to retry or move on
                    continue  # Skip to next command
            else:
                app.logger.info("Command executed successfully.")

        # Return successful result
        return jsonify({'status': 'success', 'output': task_manager.get_task_result()}), 200

    except Exception as e:
        app.logger.exception("An error occurred in /execute-task")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

