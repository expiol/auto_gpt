
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv("api_keys.env", override=True)  
DEFAULT_OPENAI_API_BASE = "https://api.openai.com/v1"
from Tools.ShellTool import tools  
from AutoAgent.AutoGPT import AutoGPT

from langchain_openai.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

def main():

    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_api_base = os.getenv("OPENAI_BASEURL") or DEFAULT_OPENAI_API_BASE

    if not openai_api_key :
        print("请在 'api_keys.env' 文件中设置 'OPENAI_API_KEY' ")
        return

    # 初始化语言模型
    llm = ChatOpenAI(
        model_name="gpt-4o",
        openai_api_key=openai_api_key,
        openai_api_base=openai_api_base
    )
    prompts_path = "./Prompts"

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

    # 选择模式
    while True:
        mode = input("请选择模式：1. 全自动 2. 人工检查 (输入 '1' 或 '2'):\n>>> ").strip()
        if mode == '1':
            manual = False
            break
        elif mode == '2':
            manual = True
            break
        else:
            print("无效输入，请输入 '1' 或 '2'。")

    # 初始化智能代理
    agent = AutoGPT(
        llm=llm,
        prompts_path=prompts_path,
        tools=tools,
        memory_retriever=retriever,
        manual=manual
    )

    while True:
        task = input("请输入您的网络安全问题（输入 'quit' 退出）：\n>>> ")
        if task.strip().lower() == "quit":
            print("程序已退出。")
            break
        reply = agent.run(task_description=task, verbose=True)
        print(f"\n回复：\n{reply}\n")

if __name__ == '__main__':
    main()