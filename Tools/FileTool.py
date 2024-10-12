from langchain.agents.agent_toolkits import FileManagementToolkit

# 用于与本地文件交互的工具包
file_toolkit = FileManagementToolkit(
    root_dir="./temp"  # 您可以根据需要更改根目录
)