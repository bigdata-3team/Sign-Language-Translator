# coding: utf-8

import requests
import time
from bs4 import BeautifulSoup
import lxml
import pandas as pd
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, select, insert
import json

url = 'https://map.naver.com/v5/api/search'

params = {
    'caller': 'pcweb',
    'query': '농아인',
    'type': 'place',
    'searchCoord': '127.0406198501587;37.51741907323963',
    'page': '1',
    'displayCount': '20',
    'isPlaceRecommendationReplace': 'true',
    'lang': 'ko'
}

params['page'] = 1
resp = requests.get(url, params=params)
dom = BeautifulSoup(resp.text, 'html.parser')


json_obj = json.loads(resp.text)

url = 'https://map.naver.com/v5/api/search'
k = 1
params = {
    'caller': 'pcweb',
    'query': '농아인',
    'type': 'place',
    'searchCoord': '127.0406198501587;37.51741907323963',
    'page': 'k',
    'displayCount': '20',
    'isPlaceRecommendationReplace': 'true',
    'lang': 'ko'
}

second=[]
while True:
    params['page'] = k
    time.sleep(1)
    resp = requests.get(url, params=params)
    json_obj = json.loads(resp.text)

    for i in json_obj['result']['place']['list']:
        first=[]
        first.append(i['name'])
        first.append(i['category'])
        first.append(i['x'])
        first.append(i['y'])
        first.append(i['address'])

        second.append(first)

    k += 1
    
    if len(json_obj['result']['place']['list']) == 0:
        break
        
df_1 = pd.DataFrame(second)
category = df_1[1].values
category = category.tolist(); category

for i in range(len(category)):
    element = category[i]
    ctg = ""
    for j in range(len(element)):
        ctg += element[j]
        if j != (len(element) - 1):
            ctg +=","
    category[i] = ctg
category

df_1["Category"] = category

del df_1[1]

df_1.columns = ["Name", "Longitude", "Latitude", "Address", "Category"]

order = ["Name", "Category", "Longitude", "Latitude", "Address"]
df_1 = df_1[order]

conn = sqlite3.connect('naver_map.db')
cur = conn.cursor()
df_1.to_sql('naver_map', conn)

cur.close()
