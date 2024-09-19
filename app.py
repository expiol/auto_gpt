from flask import Flask, request, jsonify, Response
from task_manager import TaskManager
import logging
from logging_config import setup_logging

app = Flask(__name__)
setup_logging()
task_manager = TaskManager()

@app.before_request
def log_request_info():
"""
Log request information before processing the request.
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
Log response information after processing the request.
"""
# Try to get the response data and decide how to log it based on the Content-Type
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
def execute_task():
"""
Endpoint for executing tasks. Accepts a task description and a model name, executes the task and returns a summary as plain text.
"""
try:
data = request.get_json()

if not data:
app.logger.error("No JSON data provided in the request.")
return jsonify({'status': 'error', 'message': 'No JSON data provided.'}), 400

task_description = data.get('task_description')
model_name = data.get('model_name', 'gpt-4') # defaults to gpt-4

if not task_description:
app.logger.error("Task description missing in request.")
return jsonify({'status': 'error', 'message': 'Task description is required.'}), 400

app.logger.info(f"Initialize task, description: {task_description}, model: {model_name}")

# Initialize task with selected model
task_manager.initialize_task(task_description, model_name)

# Execute commands until the task is complete
while not task_manager.is_task_complete():
success, output = task_manager.execute_next_command()

if not success:
app.logger.warning(f"Failed to execute command. Output: {output}")
# Handle errors as needed, such as retry or abort
continue

# Summarize task results using GPT
summarized_result = task_manager.summarize_task_result_with_gpt()
app.logger.debug(f"Original summary result: {summarized_result}")

# Replace escaped newlines with actual newlines for better readability
formatted_summary = summarized_result.replace("\\n", "\n").replace("\\\\n", "\n")
app.logger.debug(f"Formatted summary: {formatted_summary}")

# Return summary as plain text response
return Response(
formatted_summary,
mimetype='text/plain; charset=utf-8',
status=200
)

except Exception as e:
app.logger.exception("An error occurred at the /execute-task endpoint.")
return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
# In production environments, it is recommended to use a production-grade server (such as Gunicorn) to deploy Flask applications
app.run(host='0.0.0.0', port=8080, debug=False)
