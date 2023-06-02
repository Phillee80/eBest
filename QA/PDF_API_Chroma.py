# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from flask import Flask
from flask import request
from flask_cors import *
import traceback
import json
import logging
import requests
import time
from time import strftime, localtime
import os
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain import OpenAI
from langchain import HuggingFaceHub






app = Flask(__name__)
CORS(app, supports_credentials=True)
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 设置环境变量
os.environ['DOTENV_FILE_PATH'] = 'C:/Python'
load_dotenv()


# Get the Variables from the .env file
OPENAI_API_KEY = os.getenv('OPEN_AI_KEY')

# 使用OpenAI embedding
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 使用Hugging Face Embedding
"""
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

#Sentences we want to encode. Example:
sentence = ['This framework generates embeddings for each input sentence']


#Sentences are encoded by calling model.encode()
embedding = model.encode(sentence)
"""

# 使用OpenAI LLM
llm = OpenAI(temperature=0.2)



# Load the documents and create the index at startup
loader = PyPDFLoader("C:/Python/FAQ.pdf")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
db = Chroma.from_documents(texts, embeddings)
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":2})

def answer_questions(pdfquestion, retriever):    
    # create a chain to answer questions 
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=False)
    FinalQuestion = "你是一个专业的客服人员，回答用户提问时请注意以下3点：1.如果在文档里搜索不到相关的答案，请返回：对不起，您的问题我无法回答，请联系人工客服，2.绝对不要直接返回搜索后的原文，需要将回答概括整理后再返回，不要有语病，3.如果你认为你找到了相关答案，就不要输出请联系客服相关的话术" + pdfquestion 

    #提问
    result = qa({"query": FinalQuestion})     
    return result


@app.route('/api/chatgpt/v2', methods=['GET', 'POST'])
def extract_info():
    code = 200
    log_text = ""
    answer = ""
    elapse = ""
    try:
        request_data = json.loads(request.get_data(as_text=True))
        st = time.time()
        answer = answer_questions(request_data["question"],retriever)  
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
    with open("log.txt", "a+", encoding="utf8") as f:
        f.write("\nService on port 5200 started ^_-\n" + strftime("%Y-%m-%d %H:%M:%S", localtime()) + "\n")
    app.run(host='0.0.0.0', port=5200, processes=True)  # threaded=True
