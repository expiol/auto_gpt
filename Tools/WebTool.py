from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.document_loaders import SeleniumURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

def read_url(url: str) -> List[Document]:
    # windows下谷歌有点bug（我的环境），换成firefox
    loader = SeleniumURLLoader(browser="firefox",urls=[url],arguments=["--ignore-certificate-errors","--ignore-ssl-error"])  #自动化测试工具，模拟浏览器
    docs = loader.load()
    return docs

def read_webpage(url:str, query:str) -> str:
    """用于从网页中读取文本内容"""
    raw_doces = read_url(url)
    if len(raw_doces) == 0:
        raise "Sorry, I can't read the webpage."
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 10, #重叠字符串(0,200),(150,350),(300,500) ... 保证语义连续，每一部分的信息可以完整保留，不会因为截断丢失信息
        length_function=len,
        add_start_index = True,
    )
    paragraphs = text_splitter.create_documents([page.page_content for page in raw_doces]) #注意传递数组过来，直接传递字符串会被转成多个字符串数组
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    db = FAISS.from_documents(paragraphs, embeddings)    
    docs = db.similarity_search(query,k=1)
    return docs[0].page_content

if __name__ == "__main__":
    url = "https://www.baidu.com"
    query = "百度"
    print(read_webpage(url, query))