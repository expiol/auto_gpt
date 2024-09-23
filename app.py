from flask import Flask, request, jsonify, Response
from task_manager import TaskManager
import logging
from logging_config import setup_logging
from socketio_instance import socketio  # Import socketio from the new module

app = Flask(__name__)
setup_logging()
task_manager = TaskManager()

socketio.init_app(app)  # Initialize SocketIO with the app

@app.before_request
def log_request_info():
    """
    Log request information before processing.
    """
    try:
        data = request.get_json()
    except Exception:
        data = None
    app.logger.info(
        f"Received {request.method} request at {request.path} with data: {data}"
    )

@app.after_request
def log_response_info(response):
    """
    Log response information after processing.
    """
    if response.content_type.startswith('application/json'):
        try:
            data = response.get_json()
        except Exception:
            data = response.get_data(as_text=True)
    elif response.content_type.startswith('text/plain'):
        data = response.get_data(as_text=True)
    else:
        data = response.get_data(as_text=True)
    
    app.logger.info(
        f"Responded with status {response.status_code} and data: {data}"
    )
    return response

@app.route('/execute-task', methods=['POST'])
def execute_task_endpoint():
    """
    Endpoint to execute a task. Accepts task description and model name,
    executes the task, and returns a summary as plain text.
    """
    try:
        data = request.get_json()

        if not data:
            app.logger.error("No JSON data provided in the request.")
            return jsonify({'status': 'error', 'message': 'No JSON data provided.'}), 400

        task_description = data.get('task_description')
        model_name = data.get('model_name', 'gpt-4')  # Default to gpt-4

        if not task_description:
            app.logger.error("Task description is missing in the request.")
            return jsonify({'status': 'error', 'message': 'Task description is required.'}), 400

        app.logger.info(f"Initializing task with description: {task_description}, model: {model_name}")

        # Initialize the task with the selected model
        task_manager.initialize_task(task_description, model_name)

        def run_task():
            while not task_manager.is_task_complete():
                success, output = task_manager.execute_next_command()
                if not success:
                    app.logger.warning(f"Command execution failed: {output}")
                    continue  # Depending on requirements, handle the error (retry, abort, etc.)

            # Summarize the task result using GPT
            summarized_result = task_manager.summarize_task_result_with_gpt()
            app.logger.debug(f"Original summary result: {summarized_result}")

            # Format the summary for better readability
            formatted_summary = summarized_result.replace("\\n", "\n").replace("\\\\n", "\n")
            app.logger.debug(f"Formatted summary: {formatted_summary}")

            # Emit the task summary to clients
            socketio.emit('task_summary', {'summary': formatted_summary})

        # Run the task in a separate thread
        import threading
        thread = threading.Thread(target=run_task)
        thread.start()

        return jsonify({'status': 'success', 'message': 'Task execution started.'}), 200

    except Exception as e:
        app.logger.exception("Error occurred in /execute-task endpoint.")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/commands', methods=['GET'])
def get_commands():
    """
    Endpoint to get the current command list.
    """
    commands = task_manager.get_command_list()
    return jsonify({'status': 'success', 'commands': commands}), 200

@app.route('/commands', methods=['PUT'])
def update_commands():
    """
    Endpoint to update the command list.
    """
    data = request.get_json()
    if not data or 'commands' not in data:
        return jsonify({'status': 'error', 'message': 'No commands provided.'}), 400

    new_commands = data['commands']
    task_manager.set_command_list(new_commands)
    return jsonify({'status': 'success', 'message': 'Command list updated.'}), 200

@app.route('/pause-task', methods=['POST'])
def pause_task():
    """
    Endpoint to pause the task.
    """
    task_manager.pause()
    return jsonify({'status': 'success', 'message': 'Task paused.'}), 200

@app.route('/resume-task', methods=['POST'])
def resume_task():
    """
    Endpoint to resume the task.
    """
    task_manager.resume()
    return jsonify({'status': 'success', 'message': 'Task resumed.'}), 200

@app.route('/skip-command', methods=['POST'])
def skip_command():
    """
    Endpoint to skip the next command.
    """
    task_manager.skip()
    return jsonify({'status': 'success', 'message': 'Next command will be skipped.'}), 200

@app.route('/discuss', methods=['POST'])
def discuss():
    """
    Endpoint to discuss with GPT during a pause.
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'status': 'error', 'message': 'No message provided.'}), 400

    user_message = data['message']
    response = task_manager.discuss_with_gpt(user_message)
    return jsonify({'status': 'success', 'response': response}), 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
