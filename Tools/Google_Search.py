# CustomSearchTool.py

import os
import requests
from langchain.tools import Tool
from pydantic import BaseModel, Field

class CustomSearchInput(BaseModel):
    query: str = Field(description="要搜索的查询字符串")

def run_google_search(query: str) -> str:
    """
    使用谷歌自定义搜索 JSON API 执行搜索，并返回结果。
    这是一个备用搜索工具，当主搜索工具不可用时使用。
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        return (
            "未配置 GOOGLE_API_KEY 或 GOOGLE_SEARCH_ENGINE_ID 环境变量，"
            "无法使用备用自定义搜索工具。"
        )

    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query
    }

    try:
        response = requests.get(endpoint, params=params, timeout=10)  # 设置超时为10秒
        response.raise_for_status()
        results = response.json()

        items = results.get("items", [])
        if not items:
            return "没有找到相关结果。"

        # 格式化搜索结果
        formatted_results = []
        for item in items:
            title = item.get("title")
            link = item.get("link")
            snippet = item.get("snippet")
            formatted_results.append(f"标题: {title}\n链接: {link}\n描述: {snippet}\n")

        return "\n".join(formatted_results)

    except requests.exceptions.Timeout:
        return "请求谷歌自定义搜索超时，无法获取搜索结果。"
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP 错误发生: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"请求发生错误: {req_err}"
    except Exception as err:
        return f"发生未知错误: {err}"


google_search_tool = Tool.from_function(
    func=run_google_search,
    name="google_search",
    description=(
        "备用工具：用于通过谷歌自定义搜索 JSON API 执行网页搜索。"
        "输入一个搜索查询，返回相关的搜索结果。"
        "当主搜索工具不可用时使用。"
    ),
    args_schema=CustomSearchInput
)
