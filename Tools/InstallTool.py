import subprocess
from langchain.tools import Tool
from pydantic import BaseModel, Field
import platform

# 扩展后的允许安装的工具列表（用于网络安全和系统管理）
ALLOWED_TOOLS = [
    # 网络扫描与枚举
    'nmap', 'masscan', 'unicornscan',
    # 网络流量分析
    'tcpdump', 'wireshark', 'ngrep',
    # 网络实用工具
    'curl', 'wget', 'netcat', 'ncat', 'socat', 'hping3', 'telnet', 'ssh', 'ftp',
    # 密码破解
    'hydra', 'john', 'hashcat', 'medusa',
    # 漏洞扫描
    'nikto', 'openvas', 'lynis', 'wpscan', 'sqlmap', 'sslscan',
    # 渗透测试框架
    'metasploit', 'msfconsole', 'msfvenom', 'beef', 'empire',
    # 无线网络安全
    'aircrack-ng', 'reaver', 'kismet',
    # 网络嗅探与中间人攻击
    'ettercap', 'dsniff', 'mitmproxy',
    # Web 应用测试
    'burpsuite', 'zap', 'dirb', 'dirbuster', 'arachni',
    # 信息收集
    'whois', 'dig', 'dnsenum', 'theharvester', 'maltego',
    # 社会工程学工具
    'setoolkit',
    # 系统工具
    'strace', 'ltrace', 'lsof', 'psmisc',
    # 日志分析
    'logwatch', 'splunk',
    # 其他
    'openssh-client', 'openssl', 'nfs-common', 'rpcbind',
    # 添加更多需要的工具
]

class InstallInput(BaseModel):
    tool_name: str = Field(description="需要安装的工具名称")

def get_install_command(tool_name: str) -> str:
    os_type = platform.system()
    if os_type == 'Linux':
        # 检查发行版
        try:
            import distro
            distro_name = distro.id().lower()
        except ImportError:
            # 如果未安装 distro 库，尝试安装
            try:
                subprocess.run("pip install distro", shell=True, check=True)
                import distro
                distro_name = distro.id().lower()
            except Exception:
                # 如果仍然无法获取发行版，提示用户安装 distro 库
                raise ValueError("无法确定 Linux 发行版，请确保安装了 'distro' 库。")

        if 'ubuntu' in distro_name or 'debian' in distro_name:
            return f"sudo apt-get update && sudo apt-get install -y {tool_name}"
        elif 'centos' in distro_name or 'redhat' in distro_name or 'rhel' in distro_name or 'fedora' in distro_name:
            return f"sudo yum install -y {tool_name}"
        elif 'arch' in distro_name:
            return f"sudo pacman -S --noconfirm {tool_name}"
        elif 'alpine' in distro_name:
            return f"sudo apk add {tool_name}"
        else:
            raise ValueError(f"不支持的 Linux 发行版：{distro_name}")
    elif os_type == 'Darwin':
        # macOS
        return f"brew install {tool_name}"
    elif os_type == 'Windows':
        # Windows 系统，提示不支持
        raise ValueError("暂不支持在 Windows 系统上自动安装工具。")
    else:
        raise ValueError(f"不支持的操作系统：{os_type}")

def check_and_install_tool(tool_name: str) -> str:
    """检查工具是否已安装，如果未安装则尝试安装"""
    if tool_name not in ALLOWED_TOOLS:
        return f"不允许安装工具：{tool_name}"

    # 检查工具是否已安装
    check_command = f"which {tool_name}" if platform.system() != 'Windows' else f"where {tool_name}"
    result = subprocess.run(check_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return f"工具 {tool_name} 已安装。"

    # 尝试安装工具
    try:
        install_command = get_install_command(tool_name)
        install_result = subprocess.run(install_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return f"工具 {tool_name} 安装成功。"
    except subprocess.CalledProcessError as e:
        return f"工具 {tool_name} 安装失败：{e.stderr.strip()}"
    except ValueError as ve:
        return str(ve)
    except Exception as e:
        return f"发生未知错误：{str(e)}"

install_tool = Tool.from_function(
    func=check_and_install_tool,
    name="InstallTool",
    description="用于检查并安装所需的工具（仅限允许的工具）。请确保遵守所有适用的法律和法规，合法、道德地使用这些工具。",
    args_schema=InstallInput
)