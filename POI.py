# -*- coding: utf-8 -*-
"""
@Time ： 2023/4/24 10:15
@Auth ： Talenm
@File ：ii.py
@IDE ：PyCharm
@Motto:Art is long , life is short. 
"""
import requests
# from spacy.cli.download import get_json


def get_json(title,address,location):
    # 设置API地址和传入的数据
    api_url = 'https://apis.map.qq.com/ws/poi_association/v1'
    api_key = '2PFBZ-PHVWK-5PMJU-ATZKJ-SUNG5-6XFE3'
    title = title
    address = address
    # location = location

    # 构造请求参数
    params = {'key': api_key, 'title': title, 'address': address}

    # 发送GET请求并获取响应
    response = requests.get(api_url, params=params)

    # 检查响应状态码，200表示请求成功
    if response.status_code == 200:
        # 解析响应内容，根据API返回值的数据格式进行相应的解析
        result = response.json()
        print(result)
    else:
        # 请求失败，输出错误信息
        print('API request failed with status code:', response.status_code)
    return result

# j = get_json('上海特产超市','上海市徐汇区石龙路666号上海南站2楼候车厅','31.154016,121.429344')
# import json
# with open('l.json','w',encoding='utf8') as f:
#     g = json.dumps(j,ensure_ascii=False)
#     f.write(g)
def get_json_(title,address,location):
    # 设置API地址和传入的数据
    api_url = 'https://apis.map.qq.com/ws/poi_association/v1'
    api_key = '2PFBZ-PHVWK-5PMJU-ATZKJ-SUNG5-6XFE3'
    title = title
    address = address
    location = location

    # 构造请求参数
    params = {'key': api_key, 'title': title, 'address': address,'location': location}

    # 发送GET请求并获取响应
    response = requests.get(api_url, params=params)

    # 检查响应状态码，200表示请求成功
    if response.status_code == 200:
        # 解析响应内容，根据API返回值的数据格式进行相应的解析
        result = response.json()
        print(result)
    else:
        # 请求失败，输出错误信息
        print('API request failed with status code:', response.status_code)
    return result
import pandas as pd
from tqdm import tqdm
data = pd.read_excel('ic.xlsx')
rep = []
for i in tqdm(data.iterrows()):
    title = str(i[1]['名称'])
    address = str(i[1]['地址'])
    location = str(i[1]['纬度'])+','+str(i[1]['经度'])
    res = get_json(title,address,location)
    print ("运行到这里了")
    if res['result']['data']:
        v = res['result']['data'][0]['reliability']
    else:
        v = ''
    rep.append(v)
rep_no = []
for i in tqdm(data.iterrows()):
    title = str(i[1]['名称'])
    address = str(i[1]['地址'])
    location = str(i[1]['纬度'])+','+str(i[1]['经度'])
    res = get_json_(title,address,location)
    if res['result']['data']:
        v = res['result']['data'][0]['reliability']
    else:
        v = ''
    rep_no.append(v)

data['不增加经纬度置信度'] = rep
data['不增加经纬度置信度'] = rep_no
data.to_excel('./ic_0.xlsx')

