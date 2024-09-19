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
    在处理请求前记录请求信息。
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
    在处理完请求后记录响应信息。
    """
    # 尝试获取响应数据，根据 Content-Type 决定如何记录
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
    执行任务的端点。接受任务描述和模型名称，执行任务并返回摘要作为纯文本。
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

        # 使用选择的模型初始化任务
        task_manager.initialize_task(task_description, model_name)

        # 执行命令直到任务完成
        while not task_manager.is_task_complete():
            success, output = task_manager.execute_next_command()

            if not success:
                app.logger.warning(f"执行命令失败。输出: {output}")
                # 根据需求处理错误，例如重试或中止
                continue

        # 使用 GPT 总结任务结果
        summarized_result = task_manager.summarize_task_result_with_gpt()
        app.logger.debug(f"原始摘要结果: {summarized_result}")

        # 替换转义的换行符为实际换行符，以提高可读性
        formatted_summary = summarized_result.replace("\\n", "\n").replace("\\\\n", "\n")
        app.logger.debug(f"格式化后的摘要: {formatted_summary}")

        # 返回摘要作为纯文本响应
        return Response(
            formatted_summary,
            mimetype='text/plain; charset=utf-8',
            status=200
        )

    except Exception as e:
        app.logger.exception("在 /execute-task 端点发生错误。")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

