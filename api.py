from .Tools.ShellTool import tools  
from .AutoAgent.AutoGPT import AutoGPT

from langchain_openai.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

import os

DEFAULT_OPENAI_API_BASE = "https://api.openai.com/v1"

def get_AutoGPT():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_api_base = os.getenv("OPENAI_BASEURL") or DEFAULT_OPENAI_API_BASE

    if not openai_api_key :
        print("请在 'api_keys.env' 文件中设置 'OPENAI_API_KEY' ")
        return

    # 初始化语言模型
    llm = ChatOpenAI(
        model_name="gpt-4o-ca",
        openai_api_key=openai_api_key,
        openai_api_base=openai_api_base
    )
    prompts_path = "./action/Prompts"

    # 初始化嵌入模型
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=openai_api_key,
        openai_api_base=openai_api_base
    )

    # 初始化向量数据库，用于长时记忆
    db = FAISS.from_documents(
        [Document(page_content="")],
        embeddings
    ) 
    retriever = db.as_retriever()

    agent = AutoGPT(
        llm=llm,
        prompts_path=prompts_path,
        tools=tools,
        memory_retriever=retriever,
        manual=True
    )
    return agent

