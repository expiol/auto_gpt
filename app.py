from flask import Flask, request, jsonify
from task_manager import TaskManager
from error_handler import handle_errors
import logging

app = Flask(__name__)
task_manager = TaskManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

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

        # Set a maximum number of retries to prevent infinite loops
        max_retries = 5
        retries = 0

        # Execute commands until completion
        while not task_manager.is_task_complete():
            success, output = task_manager.execute_next_command()

            if not success:
                # Handle errors, including tool installation
                error_handled = handle_errors(output)
                if error_handled:
                    app.logger.info("Error handled by installing missing tool.")
                    continue  # Retry the current command
                else:
                    # Use GPT to analyze the error and suggest fixes
                    suggestion = task_manager.analyze_error_with_gpt(output)
                    # Try to apply the suggestion
                    applied = task_manager.apply_suggestion(suggestion)
                    retries += 1
                    if retries >= max_retries:
                        return jsonify({
                            'status': 'error',
                            'message': 'Failed to execute command after multiple retries.',
                            'error_output': output,
                            'suggestion': suggestion,
                            'command': task_manager.get_current_command()
                        }), 500
                    else:
                        app.logger.info(f"Applied suggestion from GPT. Retrying command. Retry {retries}/{max_retries}.")
                        continue
            else:
                # Reset retries if command succeeds
                retries = 0

        # Return successful result
        return jsonify({'status': 'success', 'output': task_manager.get_task_result()}), 200

    except Exception as e:
        app.logger.exception("An error occurred in /execute-task")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
