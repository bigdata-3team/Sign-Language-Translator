#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import time
from bs4 import BeautifulSoup
import lxml
import pandas as pd
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, select, insert


# In[2]:


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


# In[3]:


params['page'] = 1
resp = requests.get(url, params=params)


# In[4]:


resp.status_code


# In[5]:


dom = BeautifulSoup(resp.text, 'html.parser')


# In[6]:


import json
json_obj = json.loads(resp.text)
json_obj['result']


# In[7]:


json_obj.keys()


# In[8]:


json_obj['result'].keys()


# In[9]:


json_obj['result']['place'].keys()


# In[10]:


len(json_obj['result']['place']['list'])


# In[11]:


url = 'https://map.naver.com/v5/api/search'

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

k = 1


# In[12]:


second=[]
while True:
    params['page'] = k
    time.sleep(1)
    resp = requests.get(url, params=params)
    json_obj = json.loads(resp.text)

    for i in json_obj['result']['place']['list']:
        first=[]
#         print(i['name'])
        first.append(i['name'])
#         print(i['category'])
        first.append(i['category'])
#         print(i['x'])
        first.append(i['x'])
#         print(i['y'])
        first.append(i['y'])
#         print(i['address'], '\n')
        first.append(i['address'])

        second.append(first)

    k += 1
    
    if len(json_obj['result']['place']['list']) == 0:
        break


# In[13]:


second


# In[14]:


df_1 = pd.DataFrame(second)
category = df_1[1].values


# In[15]:


category


# In[16]:


category = category.tolist(); category


# In[17]:


for i in range(len(category)):
    element = category[i]
    ctg = ""
    for j in range(len(element)):
        ctg += element[j]
        if j != (len(element) - 1):
            ctg +=","
    category[i] = ctg
category


# In[18]:


df_1["Category"] = category
df_1


# In[19]:


del df_1[1]
df_1


# In[20]:


df_1.columns = ["Name", "Longitude", "Latitude", "Address", "Category"]
df_1


# In[21]:


order = ["Name", "Category", "Longitude", "Latitude", "Address"]
df_1 = df_1[order]
df_1


# In[22]:


conn = sqlite3.connect('naver_map.db')
cur = conn.cursor()
df_1.to_sql('naver_map', conn)


# In[23]:


cur.close()


# In[ ]:




