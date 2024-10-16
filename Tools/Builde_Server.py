import http.server    
import os
from langchain.tools import StructuredTool
from pydantic.v1 import BaseModel, Field

class BuildServerInput(BaseModel):
    port: int = Field(description="The port number to listen on")

def build_server(port: int) -> str:
    """
    在相对目录/server下的指定端口上启动一个简单的 HTTP 服务器，并返回服务器地址。
    """
    current_dir = os.getcwd()
    server_dir = os.path.join(current_dir, "server")
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=server_dir, **kwargs)
    
    server = http.server.HTTPServer(("", port), CustomHandler)
    server_address = f"http://localhost:{port}"
    return f"服务器已在 {server_address} 启动，服务目录为 {server_dir}"

build_server_tool = StructuredTool.from_function(
    func=build_server,
    name="build_server",
    description="在相对目录/server下的指定端口上启动一个简单的 HTTP 服务器，并返回服务器地址。",
    args_schema=BuildServerInput
)
