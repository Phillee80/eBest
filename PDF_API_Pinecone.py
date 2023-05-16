# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from flask import Flask
from flask import request
from flask_cors import *
import traceback
import json
import logging
import time
import os
import pinecone
import requests
import mimetypes
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader,
    WebBaseLoader,
)


app = Flask(__name__)
CORS(app, supports_credentials=True)
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
conf = json.load(open("config.json"))

# 设置环境变量
os.environ['DOTENV_FILE_PATH'] = 'C:/Python'

load_dotenv()


# Get the Variables from the .env file
OPENAI_API_KEY = os.getenv('OPEN_AI_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')


embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
chat = ChatOpenAI(temperature=0.1, openai_api_key=OPENAI_API_KEY)


class PineconeManager:
    def __init__(self, api_key, environment):
        pinecone.init(
            api_key=api_key,
            environment=environment
        )

    def list_indexes(self):
        return pinecone.list_indexes()

    def create_index(self, index_name, dimension, metric):
        pinecone.create_index(name=index_name, dimension=dimension, metric=metric)

    def delete_index(self, index_name):
        pinecone.deinit()


class DocumentLoaderFactory:
    @staticmethod
    def get_loader(file_path_or_url):
        
        
        mime_type, _ = mimetypes.guess_type(file_path_or_url)

        if mime_type == 'application/pdf':
            return PyPDFLoader(file_path_or_url)
        elif mime_type == 'text/csv':
            return CSVLoader(file_path_or_url)
        elif mime_type in ['application/msword',
                            'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return UnstructuredWordDocumentLoader(file_path_or_url)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")


class PineconeIndexManager:
    def __init__(self, pinecone_manager, index_name):
        self.pinecone_manager = pinecone_manager
        self.index_name = index_name

    def index_exists(self):
        active_indexes = self.pinecone_manager.list_indexes()
        return self.index_name in active_indexes

    def create_index(self, dimension, metric):
        self.pinecone_manager.create_index(self.index_name, dimension, metric)

    def delete_index(self):
        self.pinecone_manager.delete_index(self.index_name)

def answer_questions(pdfquestion):
    messages = [
        SystemMessage(
            content='I want you to act as a document that I am having a conversation with. Your name is "AI '
                    'Assistant". You will provide me with answers from the given info. If the answer is not included, '
                    'say exactly "Hmm, I am not sure." and stop after that. Refuse to answer any question not about '
                    'the info. Never break character.')
    ]
    
    
    docs = pinecone_index.similarity_search(query=pdfquestion, k=1)       
    main_content = pdfquestion + "\n\n"
    for doc in docs:
        main_content += doc.page_content + "\n\n"

    messages.append(HumanMessage(content=main_content))
    ai_response = chat(messages).content
    messages.pop()
    messages.append(HumanMessage(content=pdfquestion))
    messages.append(AIMessage(content=ai_response))

    return ai_response



@app.route('/api/chatgpt/v2', methods=['GET', 'POST'])
def extract_info():
    code = 200
    log_text = ""
    answer = ""
    elapse = ""
    try:
        request_data = json.loads(request.get_data(as_text=True))
        st = time.time()
        answer = answer_questions(request_data["question"])  
        elapse = f"{round(time.time() - st, 3)} s"
        msg = "成功"
    except Exception as e:
        log_text += "exception args: {args}".format(args=e.args)  # 异常信息
        log_text += traceback.format_exc() + "\n"  # 异常详细信息
        code = 500
        msg = "服务器内部错误！"
    data = {"answer": answer, "elapse": elapse}
    response = json.dumps({"code": code, "msg": msg, "data": data}, ensure_ascii=False)
    log_text += "\nreturned data: \n\t{data}".format(data=data)  # 接口返回数据
    logging.info(log_text)
    return response


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    pinecone_manager = PineconeManager(PINECONE_API_KEY, PINECONE_ENVIRONMENT)
    pinecone_index_manager = PineconeIndexManager(pinecone_manager, PINECONE_INDEX_NAME)
    file_path = "C:/Python/Financial.pdf"
    name_space = "insurance"
    pinecone_index = Pinecone.from_existing_index(index_name=pinecone_index_manager.index_name,
                                                      namespace=name_space, embedding=embeddings)
    from time import strftime, localtime
    with open("log.txt", "a+", encoding="utf8") as f:
        f.write("\nService on port 5200 started ^_-\n" + strftime("%Y-%m-%d %H:%M:%S", localtime()) + "\n")
    app.run(host='0.0.0.0', port=5200, processes=True)  # threaded=True