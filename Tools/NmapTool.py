import subprocess
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, validator
import threading
import queue
import time
import re

class NmapInput(BaseModel):
    target: str = Field(description="要扫描的目标 IP 或域名")
    ports: str = Field(
        description="要扫描的端口范围，例如 '1-65535'，默认扫描所有端口",
        default="1-65535"
    )

    @validator('target')
    def validate_target(cls, v):
        ip_pattern = re.compile(
            r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        )
        domain_pattern = re.compile(
            r"^(?=.{1,253}$)(?!-)([A-Za-z0-9-]{1,63}\.)+[A-Za-z]{2,6}$"
        )
        if not ip_pattern.match(v) and not domain_pattern.match(v):
            raise ValueError("目标必须是有效的 IP 地址或域名")
        return v

    @validator('ports')
    def validate_ports(cls, v):
        if v != "1-65535":
            port_range_pattern = re.compile(r"^\d{1,5}-\d{1,5}$")
            if not port_range_pattern.match(v):
                raise ValueError("端口范围必须符合 '起始端口-结束端口' 格式，例如 '80-443'")
            start, end = map(int, v.split('-'))
            if not (1 <= start <= 65535 and 1 <= end <= 65535 and start <= end):
                raise ValueError("端口范围必须在 1 到 65535 之间，并且起始端口小于或等于结束端口")
        return v

def run_nmap_scan(target: str, ports: str = "1-65535") -> str:
    """执行 nmap 扫描，实时返回开放的端口和运行的服务"""
    try:
        # 使用列表形式构建命令，避免命令注入
        command = ["nmap", "-T4", "-p", ports, "-sV", target]
        process = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output_queue = queue.Queue()
        error_queue = queue.Queue()

        # 定义线程函数来读取输出
        def read_output(pipe, q):
            for line in iter(pipe.readline, ''):
                if line:
                    q.put(line)
            pipe.close()

        # 创建线程读取 stdout 和 stderr
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, output_queue))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, error_queue))

        stdout_thread.start()
        stderr_thread.start()

        # 实时收集输出
        output_lines = []
        error_lines = []
        while True:
            # 读取标准输出
            while not output_queue.empty():
                line = output_queue.get()
                print(line, end='')  # 实时打印输出
                output_lines.append(line)

            # 读取标准错误
            while not error_queue.empty():
                line = error_queue.get()
                print(line, end='')  # 实时打印错误
                error_lines.append(line)

            if process.poll() is not None and output_queue.empty() and error_queue.empty():
                break

            time.sleep(0.1)  # 避免占用过多 CPU

        # 等待线程结束
        stdout_thread.join()
        stderr_thread.join()

        # 处理输出，只提取开放的端口和服务信息
        output = ''.join(output_lines)
        open_ports = []
        capture = False
        for line in output.split('\n'):
            if line.startswith("PORT"):
                capture = True
                continue
            if capture:
                if line.strip() == "" or line.startswith("Nmap done"):
                    break
                # 分析每一行，确保端口是开放的
                parts = line.split()
                if len(parts) >= 3 and parts[1].lower() == "open":
                    open_ports.append(line.strip())

        if open_ports:
            result_text = f"目标 {target} 的开放端口和服务信息：\n" + "\n".join(open_ports)
        else:
            result_text = f"未发现目标 {target} 的开放端口。"

        # 限制输出长度
        MAX_OUTPUT_LENGTH = 2000
        if len(result_text) > MAX_OUTPUT_LENGTH:
            result_text = result_text[:MAX_OUTPUT_LENGTH] + "\n...结果过长，已截断。"

        return result_text

    except subprocess.CalledProcessError as e:
        return f"nmap 命令执行失败：{e.stderr.strip()}"
    except Exception as e:
        return f"执行过程中发生错误：{str(e)}"

# 创建结构化工具
nmap_tool = StructuredTool(
    name="NmapScan",
    description="用于扫描目标的开放端口和运行的服务。输入目标 IP 或域名，以及可选的端口范围。例如，端口范围默认为 '1-65535'，也可以指定其他范围如 '80-443'。",
    func=run_nmap_scan,
    args_schema=NmapInput
)
