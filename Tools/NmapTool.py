import subprocess
from pydantic.v1 import BaseModel, Field
import threading
import queue
import time
from langchain.tools import StructuredTool

class NmapInput(BaseModel):
    target: str = Field(description="要扫描的目标 IP 或域名")
    ports: str = Field(
        description="要扫描的端口范围，例如 '1-65535'，默认扫描所有端口",
        default="1-65535"
    )

def run_nmap_scan(target: str, ports: str = "1-65535") -> str:
    """执行 nmap 扫描，实时返回开放的端口和运行的服务"""
    try:
        # 构建 nmap 命令，使用 -T4 提高扫描速度，-p 指定端口范围，-sV 探测服务版本
        command = f"nmap -T4 -p {ports} -sV {target}"
        process = subprocess.Popen(
            command,
            shell=True,
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
        fingerprints = []
        capture = False
        for line in output.split('\n'):
            if line.startswith("PORT"):
                capture = True
                continue
            if capture:
                if line.strip() == "" or line.startswith("Nmap done"):
                    capture = False
                    continue
                # 分析每一行，确保端口是开放的
                parts = line.split()
                if len(parts) >= 3 and parts[1].lower() == "open":
                    open_ports.append(line.strip())
                # 检查是否有指纹信息
                if ":SF:" in line:
                    fingerprints.append(line.strip())

        result_sections = []

        if open_ports:
            ports_info = f"目标 {target} 的开放端口和服务信息：\n" + "\n".join(open_ports)
            result_sections.append(ports_info)
        else:
            result_sections.append(f"未发现目标 {target} 的开放端口。")

        if fingerprints:
            fingerprints_info = "发现的服务指纹信息（可能未被识别）：\n" + "\n".join(fingerprints)
            result_sections.append(fingerprints_info)

        result_text = "\n\n".join(result_sections)

        MAX_OUTPUT_LENGTH = 8000
        if len(result_text) > MAX_OUTPUT_LENGTH:
            # 尝试保留指纹信息
            if fingerprints:
                fingerprints_text = "\n\n".join([section for section in result_sections if "指纹信息" in section])
                if len(fingerprints_text) <= MAX_OUTPUT_LENGTH:
                    result_text = fingerprints_text + "\n...部分结果已截断。"
                else:
                    result_text = fingerprints_text[:MAX_OUTPUT_LENGTH] + "\n...结果过长，已截断。"
            else:
                result_text = result_text[:MAX_OUTPUT_LENGTH] + "\n...结果过长，已截断。"

        return result_text

    except subprocess.CalledProcessError as e:
        return f"nmap 命令执行失败：{e.stderr.strip()}"
    except Exception as e:
        return f"执行过程中发生错误：{str(e)}"

nmap_tool = StructuredTool.from_function(
    func=run_nmap_scan,
    name="NmapScan",
    description="用于扫描目标的开放端口和运行的服务。输入目标 IP 或域名，可选的端口范围。",
    args_schema=NmapInput
)
