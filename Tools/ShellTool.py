import warnings
warnings.filterwarnings("ignore")

from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool
from Tools.NetworkSecurityTool import cve_search_tool
from Tools.shell import shell_tool  # 导入 Shell 工具
from Tools.InstallTool import install_tool  # 导入安装工具
from Tools.PythonScriptTool import python_script_tool  
from Tools.NmapTool import nmap_tool  # 导入 Nmap 工具
from Tools.search_tool import search_tool
from Tools.Google_Search import custom_search_tool
# 定义可用的工具列表
tools = [
    search_tool,
    cve_search_tool,
    shell_tool,  
    install_tool,
    python_script_tool,
    nmap_tool,
    custom_search_tool,
    # 可以在此添加更多工具
]