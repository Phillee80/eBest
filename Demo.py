import requests
from flask import Flask
from flask import request
from flask_cors import *
from langchain import OpenAI
from llama_index import SimpleDirectoryReader, LangchainEmbedding, GPTListIndex,GPTSimpleVectorIndex, PromptHelper
from llama_index import LLMPredictor, ServiceContext
from llama_index import download_loader
import traceback
import json
import logging
import time
import sys
import os
from pathlib import Path


os.environ["OPENAI_API_KEY"] = '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'
app = Flask(__name__)
CORS(app, supports_credentials=True)
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
conf = json.load(open("config.json"))
log_text = ""


def ask_bot(request_data):
  global log_text
  log_text += "access parameter: {}\n".format(request_data)  # Append request_data to log_text
  headers = {
        "content-type": "application/json",
        'Authorization': "Bearer " + conf["key"]
    }
  try:
    response = index.query(request_data, response_mode="compact")
    if response.response is None:
        print("\nBot says: \n\nI'm sorry, I couldn't generate a response.\n\n\n")
    else:
        print("\nBot says: \n\n" + response.response + "\n\n\n")
    answer = response.response.strip("\n")
    return answer
  except Exception as e:
        log_text += "exception args: {}\n".format(e.args)  # Append exception args to log_text
        log_text += "exception args: {args}".format(args=e.args)  # 异常信息
        log_text += traceback.format_exc() + "\n"  # 异常详细信息
        code = 500
        msg = "Index调用错误！"



@app.route('/api/chatgpt/v2', methods=['GET', 'POST'])
def extract_info():
    code = 200
    answer = ""
    elapse = ""
    
    try:
        request_data = json.loads(request.get_data(as_text=True))
        st = time.time()              
        answer = ask_bot(request_data['messages'][0]['content'])
        elapse = f"{round(time.time() - st, 3)} s"
        msg = "成功"
    except Exception as e:
        code = 500
        msg = "服务器内部错误！"
    data = {"answer": answer, "elapse": elapse}
    response = json.dumps({"code": code, "msg": msg, "data": data}, ensure_ascii=False)
    return response

if __name__ == '__main__':       
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    app.config['JSON_AS_ASCII'] = False
    from time import strftime, localtime
    with open("log.txt", "a+", encoding="utf8") as f:
        f.write("\nService on port 5200 started ^_-\n" + strftime("%Y-%m-%d %H:%M:%S", localtime()) + "\n")
    app.run(host='0.0.0.0', port=5200, processes=True)  # threaded=True