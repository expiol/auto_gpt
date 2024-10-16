import subprocess
import sys
from langchain.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
import os
import tempfile
import shlex

class PythonScriptInput(BaseModel):
    script_code: str = Field(description="要执行的 Python 脚本代码")
    safe: bool = Field(description="是否只允许执行安全的脚本", default=False)

def run_python_script(script_code: str, safe: bool = False) -> str:
    """生成并执行 Python 脚本，返回输出"""
    try:
        # 检查脚本内容，防止危险操作
        if safe and not is_safe_script(script_code):
            return "脚本包含不安全的操作，已被拒绝执行。"

        # 在临时目录中创建脚本文件
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as temp_script:
            temp_script.write(script_code)
            temp_script_path = temp_script.name
            
        temp_script_path = os.path.abspath(temp_script_path)
        # 定义命令，在受限环境中执行脚本（例如，使用虚拟环境或沙箱）
        python_executable = sys.executable
        command = f'"{python_executable}" "{temp_script_path}"'

        # 执行命令，捕获输出和错误
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 删除临时脚本文件
        os.unlink(temp_script_path)

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            return output if output else "脚本执行完成，但没有输出。"
        else:
            return f"脚本执行失败：{error}"

    except Exception as e:
        return f"脚本执行过程中发生异常：{str(e)}"

def is_safe_script(script_code: str) -> bool:
    """检查脚本是否安全，防止执行危险操作"""
    # 定义不安全的关键字列表
    unsafe_keywords = [
        'os.system', 'subprocess', 'eval', 'exec', 'open', '__import__',
        'sys.exit', 'shutil', 'os.remove', 'os.rmdir', 'os.unlink',
        'pickle', 'socket', 'ftplib', 'requests', 'urllib', 'input',

    ]

    # 检查脚本中是否包含不安全的关键字
    for keyword in unsafe_keywords:
        if keyword in script_code:
            return False

    return True

python_script_tool = StructuredTool.from_function(
    func=run_python_script,
    name="PythonScript",
    description="用于生成并执行 Python 脚本。请注意，脚本中不允许包含危险操作，否则将被拒绝执行。",
    args_schema=PythonScriptInput
)
