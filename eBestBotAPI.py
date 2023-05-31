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


app = Flask(__name__)
CORS(app, supports_credentials=True)
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
openai.api_key  = "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"


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0.1):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
    )
    return response.choices[0].message["content"]

def ask_bot(request_data):
  question = []
  question.append({'role':'user', 'content':f"{request_data}"})
  log_text = "access parameter: {}\n".format(request_data)  # Append request_data to log_text
  headers = {
        "content-type": "application/json",
        'Authorization': "Bearer " + openai.api_key
    }
  try:
    response = get_completion_from_messages(question) 
    print ("用户的问题是：" + request_data)
    print ("GPT的回答是：" + response)
    return response
  except Exception as e:
        log_text += "exception args: {}\n".format(e.args)  # Append exception args to log_text
        log_text += "exception args: {args}".format(args=e.args)  # 异常信息
        log_text += traceback.format_exc() + "\n"  # 异常详细信息
        code = 500
        msg = "Index调用错误！"



@app.route('/api/chatgpt/v2', methods=['GET', 'POST'])
def extract_info():
    code = 200
    log_text = ""
    answer = ""
    elapse = ""
    try:
        request_data = json.loads(request.get_data(as_text=True))
        st = time.time()
        answer = ask_bot(request_data['messages'][0]['content'])
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