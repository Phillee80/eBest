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
import openai
import os
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter


app = Flask(__name__)
CORS(app, supports_credentials=True)
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.environ['OPENAI_API_KEY'] = "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"



@app.route('/api/chatgpt/v2', methods=['GET', 'POST'])
def extract_info():
    code = 200
    log_text = ""
    answer = ""
    elapse = ""

    print ("收到请求没？")
    #嵌入问答代码
    # loader = PyPDFLoader("C:/Python/FAQ.pdf")
    # loader = UnstructuredPowerPointLoader("C:/Users/phil.li/Desktop/Product.pptx")
    loader = UnstructuredWordDocumentLoader("C:/Users/phil.li/Desktop/产品手册_脆脆鲨.docx")
    # load document
    documents = loader.load()
    # split the documents into chunks
    text_splitter = CharacterTextSplitter(separator = "[/END]", chunk_size=5, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    print ("拆分的文档数量:", len(texts) ) 
    
    # select which embeddings we want to use
    embeddings = OpenAIEmbeddings()
    # create the vectorestore to use as the index
    db = Chroma.from_documents(texts, embeddings)
    # expose this index in a retriever interface
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":5})

    prompt_template = """
                        你是一个智能问答的小助手，
                        请根据以下信息： {context}
                        回答用户的问题: {question} 
                        你只负责回答文档里包含的问题答案，如果用户的问题找不到答案，或者和文档无关，就礼貌得回答用户："对不起，知识库里检索不到问题相关的答案"。一定不要编造问题的答案。
                        当你确定能回答用户问题的时候，需要在回答的结尾添加文档中提到的图文链接。"""


    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"]) 
    chain_type_kwargs = {"prompt": PROMPT}  # 创建字典对象

    # create a chain to answer questions 
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(model_name="gpt-3.5-turbo"), chain_type="stuff", retriever=retriever, return_source_documents=False,chain_type_kwargs=chain_type_kwargs)
    
    # prompt = PromptTemplate(**chain_type_kwargs, embeddings=embeddings)  # 将嵌入式传递给 PromptTemplate
    # print("调用 OpenAI 的 prompt：", PROMPT.template)

    # chat (qa, PROMPT)


    try:
        request_data = json.loads(request.get_data(as_text=True))
        st = time.time()
        answer = qa({"query": request_data['messages'][0]['content']})
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
    from time import strftime, localtime
    with open("log.txt", "a+", encoding="utf8") as f:
        f.write("\nService on port 5200 started ^_-\n" + strftime("%Y-%m-%d %H:%M:%S", localtime()) + "\n")
    app.run(host='0.0.0.0', port=5200, processes=True)  # threaded=True


    