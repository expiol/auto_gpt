from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool

# 加载 SERPAPI 搜索工具
search = SerpAPIWrapper()
search_tool = Tool.from_function(
    func=search.run,
    name="Search",
    description="Used to search for information on the Internet through search engines"
)