# !/usr/bin/python
# -*- coding: utf-8 -*-


from flask import Flask
from flask_sslify import SSLify
from flask import request
from flask_cors import *
import traceback
import json
import logging
import time
import openai
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent
from langchain.agents import Tool
import datetime
import requests
import OrderRobot
import os
import ssl



app = Flask(__name__)
CORS(app, supports_credentials=True)
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
OPENAI_API_KEY  = "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"
# os.environ["LANGCHAIN_TRACING"] = "true"

llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    temperature=0,
    model_name='gpt-3.5-turbo'
)
# initialize conversational memory
conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True
)

# 获取当前日期
current_date = datetime.date.today()

# 将日期格式化为字符串
date_string = current_date.strftime('%Y-%m-%d')


#构造月份查询Chain
MonthPrompt=PromptTemplate(
    input_variables=["query"],
    template="今天是"+ date_string +"，用户的输入是：{query}，将用户的输入转换成月份数字并返回，不要回复推理过程，仅返回月份数字"
)
QueryMonth = LLMChain(llm=llm,prompt=MonthPrompt)

#构造日期查询Chain
DatePrompt=PromptTemplate(
    input_variables=["query"],
    template="今天是"+ date_string +"，用户的输入是：{query}，将用户的输入转换成日期数字并返回，注意仅返回YYYY-MM-DD格式的日期数字"
)
QueryDate = LLMChain(llm=llm,prompt=DatePrompt)

#构造用户意图查询Chain
ConfirmPrompt=PromptTemplate(
    input_variables=["query"],
    template="用户输入的文字是：{query}，判断用户的意图是肯定或否定，如果是肯定则回答1，如果是否定则回答0，最终输出时只输出数字。"
)
QueryConfirm = LLMChain(llm=llm,prompt=ConfirmPrompt)


#构造Agent运行的提示词
sys_msg = """Assistant is a large language model trained by OpenAI.

            Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

            Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

            Today is 2023-07-03

            All reply has to be in Chinese
            
            Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
"""

# initialize agent with tools
tools =[]
agent = initialize_agent(
    agent='chat-conversational-react-description',
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=3,
    early_stopping_method='generate',
    memory=conversational_memory
)

#门店选择/确认工具
class StorePickFromList(BaseTool):
    name = "Choose a store from a store list"
    description = "这个工具用来从一组门店列表里查询和选取1家门店。" 

    def _run(
        self, query:str       
    ):
               
        return  "打印门店列表，询问用户最终选择哪家门店"

    def _arun(self,Date):
        raise NotImplementedError("This tool does not support async")

#销量查询工具
class TatgetByUserTool(BaseTool):
    name = "Search sales achievement by Month"
    description = "这个工具用来按月份查询用户的销量数据。" 

    def _run(
        self, query:str       
    ):
        #print('\n用户的问题是：'+ query)
        TargetMonth=QueryMonth.run(query)
        print ("\n\n现在开始调用SFA的API，月份参数的值为："+ TargetMonth)

        #构造API查询
        data = {'yearp': '2023', 'parm': TargetMonth}
        headers = {'x-tenant-id': 'demo'}
        UserKPIresponse = requests.post('https://isfaqas.ebestmobile.com:5000/report/dashboard/busTargetSearch', json=data,headers=headers)

        # 检查状态码
        if UserKPIresponse.status_code == 200:
            data = UserKPIresponse.json()
        else:
            print(f"Request failed with status code {UserKPIresponse.status_code}")
        return  data['data'][0]['达成_总销量']

    def _arun(self,Date):
        raise NotImplementedError("This tool does not support async")
    
    
# 线路查询工具
class RoutePlanByUserTool(BaseTool):
    name = "Search route plan by date"
    description = "根据日期查询用户在该日的拜访线路，以及拜访计划里所有门店的code,name,address"
    
    def _run(self, query: str) -> str:
        TargetDate=QueryDate.run(query)
        print ("\n\n现在开始调用SFA的API，日期参数的值为："+ TargetDate)

        #构造API查询
        data = {
            "startDate": TargetDate,
            "userCode": "zhanghua",
            "orderItems": [
                {
                    "asc": True,
                    "column": "Sequence"
                }
            ]
        }
        headers = {'x-tenant-id': 'demo'}
        RouteResponse = requests.post('https://isfaqas.ebestmobile.com:5000/portalsync/visit/searchRouteDetailByUserId', json=data,headers=headers)
        json_data = RouteResponse.json()
        storelist = json_data['data']['storeNotList']

        outputlist = ''
        # 提取出所有的code, name, address
        for store in storelist:
            code = store['code']
            name = store['name']
            address = store['address']
            print(f"Code: {code}, Name: {name}, Address: {address}")
            outputlist = outputlist + code + " " +name + " " + address
             
        return outputlist

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("暂时不支持异步")
    
#查询门店工具
class QueryCustomer(BaseTool):
    name = "Search Customer"
    description = "通过门店名称或编码查询门店，并获取门店的Code, Name, Address等信息" 

    def _run(
        self, query:str       
    ): 
        print ("\n用户要查询的门店是：" + query)
        #构造API查询
        data = {
            "objectName": "md_store",
            "conditionField":[       
                {
                    "name":"Name",
                    "condition":"like",
                    "value":query
                }
            ],
            "returnField":["ID","Code","Name","Address","Longitude","Latitude"]

        }
        headers = {'x-tenant-id': 'demo'}
        StoreQuery = requests.post('https://isfaqas.ebestmobile.com:5000/store/object/search', json=data,headers=headers)
        outputlist = ''

        # 检查状态码
        if StoreQuery.status_code == 200:
            json_data = StoreQuery.json()
            storelist = json_data['data']
            outputlist = ''

            # 提取出所有的code, name, address
            for store in storelist:
                code = store['Code']
                name = store['Name']
                address = store['Address']
                print(f"Code: {code}, Name: {name}, Address: {address}")
                outputlist = outputlist + code + name + address
            
            return  outputlist + '我需要和用户确认从以上列表里选择一家门店'
        else:
            print(f"Request failed with status code {StoreQuery.status_code}")
        
    
        '''
        print ("系统里查到包含'" + query + "'的门店有：")
        print ("第1家: 编号 00001, 名称 老王一店, 地址 大望路100号")
        print ("第2家: 编号 00002, 名称 老王二店, 地址 大望路200号")
        print ("第3家: 编号 00003, 名称 老王三店, 地址 大望路300号")
        input ("请输入您要拜访第几家门店：")
        answer = input("确认您要拜访的门店是：第2家: 编号 00002, 名称 老王二店, 地址 大望路200号\n")
        if QueryConfirm.run(answer):
            print("现在开始拜访流程")
        else: 
            print("请重新查询选择您要拜访的门店")

        return "现在开始拜访流程"
        '''
    
    def _arun(self,query:str):
        raise NotImplementedError("This tool does not support async") 
    

#查询门店函数
def FunQueryCustomer(Storename):
    print ("系统里查到包含'" + Storename + "'的门店有：")
    print ("第1家: 编号 00001, 名称 老王一店, 地址 大望路100号")
    print ("第2家: 编号 00002, 名称 老王二店, 地址 大望路200号")
    print ("第3家: 编号 00003, 名称 老王三店, 地址 大望路300号")
    input ("请输入您要拜访第几家门店：")
    answer = input("确认您要拜访的门店是：第2家: 编号 00002, 名称 老王二店, 地址 大望路200号？\n")
    if QueryConfirm.run(answer):
        print("现在开始拜访流程")
        return 1
    else: 
        print("请重新查询选择您要拜访的门店")
        return 0
       
    
#订单工具
class PlaceOrder(BaseTool):
    name = "Order Taking"
    description = "该工具实现了订单的功能" 

    def _run(
        self, query:str       
    ): 
        OrderRobot.main()
        return "现在开始调用GPT的订单功能-eBestBotAPI"

    def _arun(self,query:str):
        raise NotImplementedError("This tool does not support async") 

#拜访工具
class StartVisit(BaseTool):
    name = "Start Visit"
    description = "该工具实现了拜访的功能，开始拜访前必须明确门店的编码" 

    def _run(
        self, query:str       
    ): 
        if FunQueryCustomer(query):
            print ("现在开始拜访流程")
            #print ("现在开始拜访流程")
            return "结束"

    def _arun(self,query:str):
        raise NotImplementedError("This tool does not support async")

#构造工具集及Agent
tools = [TatgetByUserTool(),RoutePlanByUserTool(),QueryCustomer(),PlaceOrder(),StartVisit(),StorePickFromList()]
new_prompt = agent.agent.create_prompt(
    system_message=sys_msg,
    tools=tools
)
agent.agent.llm_chain.prompt = new_prompt
agent.tools = tools




@app.route('/api/chatgpt/v2', methods=['GET', 'POST'])
def extract_info():
    code = 200
    log_text = ""
    answer = ""
    elapse = ""
    try:
        request_data = json.loads(request.get_data(as_text=True))
        st = time.time()
        print("用户输入的问题是：" + request_data['messages'][0]['content'])
        answer = agent.run(request_data['messages'][0]['content'])
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
    context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain("C:/Users/phil.li/Desktop/Nginx/ebestmobile.net_cert_chain.pem", 
                            keyfile="C:/Users/phil.li/Desktop/Nginx/ebestmobile.net_key.key")
    # 将应用程序绑定到SSL上下文  
    sslify = SSLify(app)
    app.run(host="0.0.0.0", port=5200, ssl_context=context, debug=True)
    #app.run(host='0.0.0.0', port=5200, processes=True)  # threaded=True