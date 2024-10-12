import os
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool

serpapi_api_key = os.getenv("SERPAPI_API_KEY")

if serpapi_api_key:
    search = SerpAPIWrapper()
    search_tool = Tool.from_function(
        func=search.run,
        name="Search",
        description="Used to search for information on the Internet through search engines"
    )
else:
    def unavailable_search(query: str) -> str:
        return "未填入api，无法使用search工具"

    search_tool = Tool.from_function(
        func=unavailable_search,
        name="Search",
        description="未填入api，无法使用search工具"
    )

