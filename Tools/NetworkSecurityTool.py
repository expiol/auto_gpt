import requests
from langchain.tools import StructuredTool
from pydantic.v1 import BaseModel, Field

class CVEQuery(BaseModel):
    query: str = Field(description="要搜索的 CVE 编号")

def cve_search(query: str) -> str:
    """根据查询搜索 CVE 信息"""
    url = f"https://cve.circl.lu/api/cve/{query}"  # 修正 URL
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'id' in data:
            cve_info = data
            # 提取 CVE 信息
            references = ', '.join(cve_info.get('references', []))  # 修正引用提取逻辑
            return (
                f"CVE ID: {cve_info.get('id', 'N/A')}\n"
                f"摘要: {cve_info.get('summary', 'N/A')}\n"
                f"引用: {references if references else '无引用'}"
            )
        else:
            return "未找到相关的 CVE 信息。"
    else:
        return f"检索 CVE 信息时出错。状态码: {response.status_code}"

# 使用 langchain 的工具
cve_search_tool = StructuredTool.from_function(
    func=cve_search,
    name="CVE Search",
    description="根据查询搜索 CVE（公共漏洞和暴露）信息",
    args_schema=CVEQuery
)