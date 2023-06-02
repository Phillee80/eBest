import pymysql
import json
import pandas as pd
from IPython.display import display
from typing import Optional, Type
from langchain.tools import BaseTool
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from pydantic import BaseModel, Field
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
import os


os.environ['OPENAI_API_KEY'] = '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'



# 建立连接
conn = pymysql.connect(host='mysql-nfa-dev.mysql.database.chinacloudapi.cn', port=3306, db='nsfa_report', user='sa@mysql-nfa-dev', passwd='Sharepoint@adminsfa2021',
                           charset='utf8mb4')

# 创建游标
# cursor = conn.cursor()


class SearchSchema(BaseModel):
    query: str = Field(description="input store code:")

# 搜索门店
class StoreSearchTool(BaseTool):
    name = "Search Store Sales"
    description = "查询这个门店月销售统计"
    # args_schema: Type[SearchSchema] = SearchSchema
    return_direct = True  # 直接返回结果

    def _run(self, query: str) -> str:
        print("\nSearch Store Sales Query: " + query)
        #call api function


        # 执行 SELECT 语句
        # query = "select * from view_store_sales_month"
        query = "CALL sp_store_sales_month('" + query + "')"
        cursor.execute(query)

        # 获取结果集
        results = cursor.fetchall()
        conn.commit()

        # 转换为 DataFrame 格式
        df = pd.DataFrame(results, columns=["日期", "门店编号", "门店名称", "商品编码", "商品名称", "单位", "规格", "数量"])
        df.style.set_properties(**{'text-align': 'left'})

        print(df)

        # 转换为 JSON 格式
        json_results = json.dumps(results, ensure_ascii=False)


        print("去调用门店服务月销量API接口")
        return "查询月销量数据结果：\n" + json_results

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("暂时不支持异步")
    
# 搜索产品
class ProductSearchTool(BaseTool):
    name = "Search Product Item List"
    description = "查询这个门店的产品分销"
    return_direct = True  # 直接返回结果

    def _run(self, query: str) -> str:
        print("\nSearch Product Item List Query: " + query)
        #call api function

        print("去调用查询分销的API接口")
        return "查询分销数据结果：xxxxxxx"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("暂时不支持异步")

# 计算工具
class CalculatorTool(BaseTool):
    name = "Calculator"
    description = "如果是关于数学计算的问题，请使用它"

    def _run(self, query: str) -> str:
        print("\nCalculatorTool query: " + query)
        return "3"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("暂时不支持异步")

# 定位
class GPSposition(BaseTool):
    name = "GPS"
    description = "如果是关于定位或者打卡的问题，请使用它"

    def _run(self, query: str) -> str:
        print("\n现在执行定位功能 " )
        return "4"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("暂时不支持异步")


llm = OpenAI(temperature=0)
tools = [StoreSearchTool(), ProductSearchTool(), CalculatorTool()，GPSposition()]
agent = initialize_agent(
    tools, llm, agent="zero-shot-react-description", verbose=True)


question = input("请输入你的问题：")
agent.run(question)
#sqlresult = agent.run("查询门店家乐福古北月销量")
#print("结果：" + sqlresult)
#summary = llm ("基于上面的数据分析一下销量异常的产品:" + sqlresult)
#print("基于以上数据的分析结果：" + summary)

""""
print("问题2：")
print("结果：" + agent.run("查询门店小黄鸭月销量"))

print("问题3：")
print("结果：" + agent.run("查询门店10083250月销量"))

print("问题4：")
print("结果：" + agent.run("查询门店12017297月销量"))
# print("结果：" + agent.run("查询产品分销"))

"""

# 关闭游标和连接
cursor.close()
conn.close()