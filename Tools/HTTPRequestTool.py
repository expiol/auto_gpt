import requests
from langchain.tools import StructuredTool
from pydantic.v1 import BaseModel, Field
from typing import Optional

class HTTPRequestQuery(BaseModel):
    url: str = Field(description="目标 URL")
    method: str = Field(description="HTTP 方法（GET, POST, PUT, DELETE 等）")
    headers: Optional[dict] = Field(default=None, description="HTTP 请求头")
    data: Optional[str] = Field(default=None, description="请求体数据（用于 POST, PUT 等）")

def send_http_request(url: str, method: str, headers: Optional[dict] = None, data: Optional[str] = None) -> str:
    """发送 HTTP 请求并获取响应"""
    try:
        response = requests.request(method, url, headers=headers, data=data, timeout=10)
        return f"HTTP 状态码: {response.status_code}\n响应头: {dict(response.headers)}\n响应体: {response.text}..."
    except Exception as e:
        return f"发送 HTTP 请求时出错：{str(e)}"

http_request_tool = StructuredTool.from_function(
    func=send_http_request,
    name="Send HTTP Request",
    description="发送 HTTP 请求到指定 URL，并获取响应",
    args_schema=HTTPRequestQuery
)
