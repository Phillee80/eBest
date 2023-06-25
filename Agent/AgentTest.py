from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent
from langchain.agents import Tool
import datetime


OPENAI_API_KEY = "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"

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


#构造月份查询工具
MonthPrompt=PromptTemplate(
    input_variables=["query"],
    template="上下文：今天是"+ date_string +"，从用户的问题里推理出用户想要查询的月份的阿拉伯数字，问题：{query}"
)
QueryMonth = LLMChain(llm=llm,prompt=MonthPrompt)

#构造日期查询工具
DatePrompt=PromptTemplate(
    input_variables=["query"],
    template="上下文：今天是"+ date_string +"，从用户的问题里推理出用户想要查询的日期，以YYYY-MM-DD的格式返回，问题：{query}"
)
QueryDate = LLMChain(llm=llm,prompt=DatePrompt)


#构造Agent运行的提示词
sys_msg = """Assistant is a large language model trained by OpenAI.

            Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

            Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

            如果用户问题里有提到月份但是你无法明确月份具体的阿拉伯数字，使用其他tool推理出月份的阿拉伯数字后继续思考下一步行动。
            如果用户问题里提到日期不是YYYY-MM-DD的格式，使用其他tool推理出正确格式的日期数字后继续思考下一步行动。
            今天的日期是2023年6月25日

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

#销量查询工具
class TatgetByUserTool(BaseTool):
    name = "Search sales achievement by Month"
    description = "这个工具用来按月份查询用户的销量数据。在使用该工具时用户必须提供参数'月'。你在使用这个参数的时候，需要忽略'月'这个字。" 

    def _run(
        self, query:str       
    ):
        #print ("用户查询的月份是："+ query) 
        print ("\n\n现在开始调用SFA的API，月份参数的值为："+ query)
        return "用户要查询"+ query + "月的业绩，该月业绩是￥3000"

    def _arun(self,Date):
        raise NotImplementedError("This tool does not support async")
    
#确认月份工具
class ConfirmMonth(BaseTool):
    name = "Calculate the month"
    description = "用这个工具从用户的问题中找出查询月份具体的阿拉伯数字" 

    def _run(
        self, query:str       
    ): 
        return QueryMonth.run(query)

    def _arun(self,query:str):
        raise NotImplementedError("This tool does not support async")

#确认日期工具
class ConfirmDate(BaseTool):
    name = "Calculate the date"
    description = "用这个工具从用户的问题中找出具体查询的日期" 

    def _run(
        self, query:str       
    ): 
        return QueryDate.run(query)

    def _arun(self,query:str):
        raise NotImplementedError("This tool does not support async")  

    
# 线路查询工具
class RoutePlanByUserTool(BaseTool):
    name = "Search route plan by date"
    description = "根据日期查询用户在该日的拜访线路。在使用该工具时用户必须提供参数'日期'。"
    
    def _run(self, query: str) -> str:
        sql = """   SELECT
                        r.UserCode as '用户编码',
                        p.Name as '用户名称',
                        r.StoreCode as '门店编码',
                        s.Name as '门店名称',
                        r.Date as '日期',
                        r.Sequence as '顺序'
                    FROM
                        md_routedetail r
                        LEFT JOIN md_store s ON s.Code = r.StoreCode
                        LEFT JOIN md_person p ON r.UserCode = p.`Code` 
                    WHERE
                        (r.Date = %s)
                        and r.UserCode = %s
                    ORDER BY
                        r.Sequence"""
        
        Planned_date = query
        usercode = 'zhanghua'

        '''
        # 定义查询参数
        param = (formatted_date, usercode)
        cursor.execute(sql,param)

        # 获取结果集
        results = cursor.fetchall()
        connection.commit()

        # 转换为 DataFrame 格式
        df = pd.DataFrame(results, columns=["用户编码", "用户名称", "门店编码", "门店名称", "日期", "顺序"])
        df.style.set_properties(**{'text-align': 'left'})

        print(df)

        # 转换为 JSON 格式
        json_results = json.dumps(results, ensure_ascii=False, cls=DateEncoder)
        return "查询计划路线数据结果：\n" + json_results
        '''
        return "调用计划线路查询，用户想要查询的日期是：" + Planned_date

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("暂时不支持异步")
    
#查询门店工具
class QueryCustomer(BaseTool):
    name = "Search Customer"
    description = "通过门店名称或编码查询门店" 

    def _run(
        self, query:str       
    ): 
        return "用户查询的门店是：名称包含'" + query + "'或者编码包含'"+ query + "'的门店"

    def _arun(self,query:str):
        raise NotImplementedError("This tool does not support async") 
    
#订单工具
class PlaceOrder(BaseTool):
    name = "Order Taking"
    description = "该工具实现了订单的功能" 

    def _run(
        self, query:str       
    ): 
        return "现在开始调用GPT的订单功能-eBestBotAPI"

    def _arun(self,query:str):
        raise NotImplementedError("This tool does not support async") 


#构造工具集及Agent
tools = [ConfirmMonth(),TatgetByUserTool(),RoutePlanByUserTool(),QueryCustomer(),PlaceOrder()]
new_prompt = agent.agent.create_prompt(
    system_message=sys_msg,
    tools=tools
)
agent.agent.llm_chain.prompt = new_prompt
agent.tools = tools

#-------------------------以下是测试场景：------------------------------------

#场景一：查询业代销量
#agent.run("我上个月的月销量是多少？")

#场景二：查询线路
#agent.run("查一下昨天的线路") 

#场景三：查询门店
#agent.run("查门店漕河泾软件大厦罗森便利店") 

#场景四：订单功能
agent.run("下订单") 