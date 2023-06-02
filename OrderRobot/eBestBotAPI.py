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

global_context=[ {'role':'system', 'content':"""
                你是一个订单机器人，负责处理用户的订单 \
                用户给出的商品名称通常是简称，可能存在一个或多个名称相近的商品，如果你无法确认具体是哪一个商品，则提示用户并确认，但是不要过多得确认影响了用户体验确认用户在完成所有的商品的采购以后，开始计算订单金额\
                这里你需要一步一步得思考。首先计算每一个订单行的金额，再计算总金额，然后检查订单的数量或者金额是否满足了促销政策，如果满足则重新计算订单的金额。注意这里的计算步骤不要输出给用户\
				示例：用户订购A产品10个，B产品5个，先计算10个A产品金额，再计算5个B产品金额，金额相加计算总金额。然后A产品订购数量满足了满赠促销条件，则在订单行里自动加上1行赠品，且价格为0。最后检查总金额满足了满减的促销条件，则从总金额里扣除折扣的金额\
                最后计算整张订单金额，并加上6%的商品税。\
                以reciet的格式打印订单明细并请用户确认金额\
                询问客户是否对订单满意并说再见\
                You respond in a short, very conversational friendly style. \
                用户可订购的商品列表包括：\
                屈臣氏蒸馏水12L 6000001  ￥24 \
                屈臣氏蒸馏水18.9L 6000002  ￥32 \
                屈臣氏饮用矿物质水18.9L 6000003  ￥35 \
                屈臣氏饮用纯净水18.9L 6000004  ￥35 \
                水票 6000005 ￥30 \
                
                促销活动包括：
                1. 总金额（不含税）满200元，扣减10元
                2. 采购数量达到10桶赠送1桶屈臣氏蒸馏水12L

                当用户明确订单完成后，create a json summary of the previous order. Itemize the price for each item\
                The fields should be 1) 商品编号 2) 商品名称 3) 订购数量  4)total price
                """} ]


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0.1):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
    )
    return response.choices[0].message["content"]

def ask_bot(request_data):
  global global_context
  global_context.append({'role':'user', 'content':f"{request_data}"})

  log_text = "access parameter: {}\n".format(request_data)  # Append request_data to log_text
  headers = {
        "content-type": "application/json",
        'Authorization': "Bearer " + openai.api_key
    }
  try:
    print ("-------------用户的问题是：----------\n" )
    print (global_context)
    print ("-------------问题结束：----------\n" )
    response = get_completion_from_messages(global_context)

    global_context.append({'role': 'assistant', 'content': f"{response}"})


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