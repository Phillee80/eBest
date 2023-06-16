import pandas as pd
import requests
import re

# gaodekey = '3ff38452da0f55a1ba37de2ee6eb5300'
gaodekey = 'd20c1828f1bde69314703f66583d3f32'

targetpath = 'C:/Users/Phil/Desktop/data/new.xlsx'
# 读取 Excel 文件
df = pd.read_excel('C:/Users/Phil/Desktop/data/ul.xlsx')
dfnew = pd.DataFrame(columns=['code','name','address','tel','Province','City','District','Street','Longitude_Gaode','Latitude_Gaode','channel1','channel2','channel3','chains','distributor','pic','license','idcrad','errType'])
dfnewrowid = 1


def gpstolocal(v):
    province = ''
    district = ''
    url = 'https://restapi.amap.com/v3/geocode/regeo'
    params = {
        'key': gaodekey,
        'location': v
    }
    response = requests.get(url, params=params)

    print(response)

    if response.status_code == 200:
        data = response.json()
        print(data)
        if data['status'] == '1':
            province = data['regeocode']['addressComponent']['province']
            district = data['regeocode']['addressComponent']['district']

    return province,district

def addtogps(v):
    print(v)
    province = ''
    district = ''
    lng = ''
    lat = ''
    # url = 'https://restapi.amap.com/v3/geocode/geo'
    url = 'https://restapi.amap.com/v3/place/text'
    params = {
        'key': gaodekey,
        'keywords': v,
        'cityname': '上海市'
    }
    response = requests.get(url, params = params)
    print(response)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if data['status'] =='1' and data['pois'] and len(data['pois'])>0 :
            province = data['pois'][0]['pname']
            district = data['pois'][0]['adname']
            location = data['pois'][0]['location']
            locationarr = location.split(",")
            lng = locationarr[0]
            lat = locationarr[1]

    return province, district,lng,lat


def addtogps2(v):
    print(v)
    province = ''
    district = ''
    lng = ''
    lat = ''
    # url = 'https://restapi.amap.com/v3/geocode/geo'
    url = 'https://restapi.amap.com/v3/place/text'
    params = {
        'key': gaodekey,
        'keywords': v,
        'cityname': '上海市'
    }
    response = requests.get(url, params=params)
    print(response)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if data['status'] =='1' and data['pois'] and len(data['pois']) > 0:
            poisdata= data['pois']
            print(poisdata)
            poicount = 0
            for item in poisdata :
                province = item['pname']
                district = item['adname']
                location = item['location']
                locationarr = location.split(",")
                lng = locationarr[0]
                lat = locationarr[1]
                print(poicount)
                poicount+=1
                if province == '上海市' and district == '徐汇区' :
                    break

    return province, district, lng, lat

def addtogps3(v):
    print(v)
    province = ''
    district = ''
    lng = ''
    lat = ''
    url = 'https://restapi.amap.com/v3/geocode/geo'

    params = {
        'key': gaodekey,
        'address': v,
        'city': '上海市'
    }
    response = requests.get(url, params=params)
    print(response)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if data['status']=='1' and  data['geocodes'] and len(data['geocodes']) > 0:
            geodata= data['geocodes']
            poicount = 0
            for item in geodata :
                province = item['province']
                district = item['district']
                location = item['location']
                locationarr = location.split(",")
                lng = locationarr[0]
                lat = locationarr[1]
                print(poicount)
                poicount+=1
                if province == '上海市' and district == '徐汇区' :
                    break

    return province, district, lng, lat


# 循环每一行并进行计算
for index, row in df.iterrows():
    gps_province = ''
    gps_district = ''

    add_province = ''
    add_district = ''
    add_lng = ''
    add_lat = ''

    res_lng = ''
    res_lat = ''
    res_errtype= '-1'
    # 计算逻辑
    if len(str(row['Longitude_Gaode'])) > 0 and len(str(row['Latitude_Gaode'])) > 0:
        v = str(row['Longitude_Gaode'])+','+str(row['Latitude_Gaode'])
        gps_province,gps_district = gpstolocal(v)

    address = row['address']
    keywords = ["上海市", "市辖区（上海）", "徐汇区"]
    for keyword in keywords:
        address = address.replace(keyword, "")

    if len(address)>0:
        add_province,add_district,add_lng,add_lat = addtogps2(row['Province']+row['City']+row['District']+address)

    # if len(row['address'])>0:
    #     add_province,add_district,add_lng,add_lat = addtogps2(row['address'])

    if gps_province == '上海市' and gps_district == '徐汇区' and add_province == '上海市' and add_district == '徐汇区':
        res_errtype ='0'
        res_lng = str(row['Longitude_Gaode'])
        res_lat = str(row['Latitude_Gaode'])
    elif gps_province == '上海市' and gps_district == '徐汇区':
        res_errtype = '1'
        res_lng = str(row['Longitude_Gaode'])
        res_lat = str(row['Latitude_Gaode'])
    elif add_province == '上海市' and add_district == '徐汇区':
        res_errtype = '2'
        res_lng = add_lng
        res_lat = add_lat
    else:
        res_errtype = '3'


    #
    # address = row['address']
    # keywords = ["上海市", "徐汇区"]
    # pattern = re.compile(r'\b(' + '|'.join(keywords) + r')\b\s*')
    # address = pattern.sub('', address)

    address = row['address']
    keywords = ["上海市","市辖区（上海）", "徐汇区"]
    for keyword in keywords:
        address = address.replace(keyword, "")

    dfnew.loc[dfnewrowid] = [row['code'], row['name'], row['Province']+row['City']+row['District']+address, row['tel'], row['Province'], row['City'],
                             row['District'], row['Street'], res_lng, res_lat,
                             row['channel1'], row['channel2'], row['channel3'], row['chains'],
                             row['distributor'], row['pic'], row['license'], row['idcrad'],res_errtype
                             ]
    dfnewrowid += 1

# 将修改后的数据写入新的 Excel 文件
dfnew.to_excel(targetpath, index=False)

