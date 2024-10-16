import os
from langchain.tools import StructuredTool
from pydantic.v1 import BaseModel, Field

class CreateFileInput(BaseModel):
    filename: str = Field(description="要创建的文件名")
    content: str = Field(description="要创建的文件内容")
    directory: str = Field(description="创建文件的目录（可以是相对路径或绝对路径）")

def create_file(filename: str, content: str, directory: str) -> str:
    """
    在指定目录下创建一个文件，支持相对路径和绝对路径，并返回文件路径。
    """
    # 如果是相对路径，将其转换为绝对路径
    if not os.path.isabs(directory):
        directory = os.path.abspath(directory)
    
    # 确保目录存在，如果不存在则创建
    os.makedirs(directory, exist_ok=True)
    
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as file:
        file.write(content)
    return f"文件 {filename} 已成功创建在 {directory}"

create_file_tool = StructuredTool.from_function(
    func=create_file,
    name="create_file",
    description="在指定目录下创建一个文件，支持相对路径和绝对路径，并返回文件路径。",
    args_schema=CreateFileInput
)
