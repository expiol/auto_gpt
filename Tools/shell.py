# ShellTool.py

import subprocess
from langchain.tools import Tool
from pydantic import BaseModel, Field
import threading
import queue
import time

class ShellInput(BaseModel):
    command: str = Field(description="要执行的 Shell 命令")

def run_shell_command(command: str) -> str:
    """执行一般的 Shell 命令，实时返回输出"""
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        output_queue = queue.Queue()
        error_queue = queue.Queue()

        # 定义线程函数来读取输出
        def read_output(pipe, queue):
            for line in iter(pipe.readline, ''):
                queue.put(line)
            pipe.close()

        # 创建线程读取 stdout 和 stderr
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, output_queue))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, error_queue))

        stdout_thread.start()
        stderr_thread.start()

        # 实时收集输出
        output = ''
        error = ''
        while True:
            try:
                line = output_queue.get_nowait()
                output += line
                print(line, end='')  # 实时打印输出
            except queue.Empty:
                pass

            try:
                line = error_queue.get_nowait()
                error += line
                print(line, end='')  # 实时打印错误
            except queue.Empty:
                pass

            if process.poll() is not None and output_queue.empty() and error_queue.empty():
                break

            time.sleep(0.1)  # 避免占用过多 CPU

        # 等待线程结束
        stdout_thread.join()
        stderr_thread.join()

        if output.strip():
            return output.strip()
        elif error.strip():
            return f"命令执行错误：{error.strip()}"
        else:
            return "命令执行完成，但没有输出。"

    except subprocess.CalledProcessError as e:
        return f"命令执行失败：{e.stderr.strip()}"
    except Exception as e:
        return f"命令执行过程中发生异常：{str(e)}"

shell_tool = Tool.from_function(
    func=run_shell_command,
    name="Shell",
    description="用于执行一般的 Shell 命令。请谨慎使用，确保命令的安全性。",
    args_schema=ShellInput
)