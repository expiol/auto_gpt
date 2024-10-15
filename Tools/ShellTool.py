import warnings
warnings.filterwarnings("ignore")

from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool
from .NetworkSecurityTool import cve_search_tool
from .shell import shell_tool  # 导入 Shell 工具
from .InstallTool import install_tool  # 导入安装工具
from .PythonScriptTool import python_script_tool  
from .NmapTool import nmap_tool  # 导入 Nmap 工具
from .search_tool import search_tool
from .Google_Search import google_search_tool
from .HTTPRequestTool import http_request_tool  # 导入新的 HTTP 请求工具

# 定义可用的工具列表
tools = [
    search_tool,
    cve_search_tool,
    shell_tool,  
    install_tool,
    python_script_tool,
    nmap_tool,
    google_search_tool,
    http_request_tool,  # 添加新的 HTTP 请求工具
    # 可以在此添加更多工具
]
