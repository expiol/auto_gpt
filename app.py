from flask import Flask, request, jsonify, Response
from task_manager import TaskManager
import logging
from logging_config import setup_logging
from socketio_instance import socketio  # Import socketio from the new module

app = Flask(__name__)
setup_logging()
task_manager = TaskManager()

socketio.init_app(app)

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
            if data is None:
                data = response.get_data(as_text=True)
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
    接收任务描述，生成命令列表，并返回给用户确认。
    """
    try:
        data = request.get_json()

        if not data:
            app.logger.error("请求中未提供 JSON 数据。")
            return jsonify({'status': 'error', 'message': 'No JSON data provided.'}), 400

        task_description = data.get('task_description')
        model_name = data.get('model_name', 'gpt-4')  # 默认为 gpt-4

        if not task_description:
            app.logger.error("请求中缺少任务描述。")
            return jsonify({'status': 'error', 'message': 'Task description is required.'}), 400

        app.logger.info(f"初始化任务，描述: {task_description}，模型: {model_name}")

        # 使用选择的模型初始化任务，但不执行
        task_manager.initialize_task(task_description, model_name)

        # 获取生成的命令列表
        commands = task_manager.get_command_list()

        # 返回命令列表给用户确认
        return jsonify({
            'status': 'success',
            'message': 'Task initialized. Please confirm the command list before execution.',
            'commands': commands
        }), 200

    except Exception as e:
        app.logger.exception("在 /execute-task 端点发生错误。")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/confirm-task', methods=['POST'])
def confirm_task():
    """
    用户确认后开始执行任务。
    """
    try:
        # 检查是否有已初始化的任务
        if not task_manager.commands:
            return jsonify({'status': 'error', 'message': 'No task initialized to execute.'}), 400

        # 在单独的线程中运行任务
        def run_task():
            while not task_manager.is_task_complete():
                success, output = task_manager.execute_next_command()
                if not success:
                    app.logger.warning(f"命令执行失败：{output}")
                    continue  # 根据需求处理错误

            # 使用 GPT 总结任务结果
            summarized_result = task_manager.summarize_task_result_with_gpt()
            app.logger.debug(f"原始摘要结果：{summarized_result}")

            # 格式化摘要
            formatted_summary = summarized_result.replace("\\n", "\n").replace("\\\\n", "\n")
            app.logger.debug(f"格式化后的摘要：{formatted_summary}")

            # 向客户端发送任务总结
            socketio.emit('task_summary', {'summary': formatted_summary})

        # 启动任务线程
        thread = threading.Thread(target=run_task)
        thread.start()

        return jsonify({'status': 'success', 'message': 'Task execution started.'}), 200

    except Exception as e:
        app.logger.exception("在 /confirm-task 端点发生错误。")
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
    Endpoint to skip the current command.
    """
    task_manager.skip()
    return jsonify({'status': 'success', 'message': 'Current command will be skipped.'}), 200

@app.route('/discuss', methods=['POST'])
def discuss():
    """
    在任务执行前或暂停时，与 GPT 讨论并重新生成命令列表。
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'status': 'error', 'message': 'No message provided.'}), 400

    user_message = data['message']
    response = task_manager.discuss_with_gpt(user_message)

    if isinstance(response, dict) and 'commands' in response:
        return jsonify({
            'status': 'success',
            'message': 'Command list updated based on discussion.',
            'commands': response['commands']
        }), 200
    else:
        return jsonify({'status': 'success', 'response': response}), 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
