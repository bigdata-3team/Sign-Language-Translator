#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import time
from bs4 import BeautifulSoup
import lxml
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, select, insert


# In[2]:


url = 'http://www.deafkorea.com/ver/_board/list.html'

params = {
    'tb': 'Board',
    'code': 'notice',
    'keyfield': '',
    'key': '',
    'page': '1'
}
params['page'] = 2
resp = requests.get(url, params=params)
resp.encoding = 'cp949'
dom = BeautifulSoup(resp.content, 'html.parser')


# In[3]:


dom.find_all('td', attrs={'class':"sFontDate"})


# In[4]:


for _ in dom.find_all('a', attrs={'class':'board1'}):
    print('http://www.deafkorea.com/ver/_board/'+_['href'],
          '\n',_.text,'\n')


# In[5]:


for _ in dom.find_all('td', attrs={'class':"sFontDate"}):
    print(_.text)


# In[6]:


for a, b in zip(dom.find_all('a', attrs={'class':'board1'}), dom.find_all('td', attrs={'class':"sFontDate"})):
            print('http://www.deafkorea.com/ver/_board/'+a['href'],
          '\n',a.text,b.text,'\n')


# In[7]:


url = 'http://www.deafkorea.com/ver/_board/list.html'
url_i = 'http://www.deafkorea.com/ver/_board/'
params = {
    'tb': 'Board',
    'code': 'notice',
    'keyfield': '',
    'key': '',
    'page': '1'
}

page_num = 1
c = []
while True:
    params['page'] = page_num
    resp = requests.get(url, params=params)
    resp.encoding = 'cp949'
    dom = BeautifulSoup(resp.content, 'html.parser')
    for a, b in zip(dom.find_all('a', attrs={'class':'board1'}), dom.find_all('td', attrs={'class':"sFontDate"})):
            print('title:',a.text,'\ndate:',b.text,'\n',url_i+a['href'],'\n')
            c.extend([a.text, b.text, url_i+a['href']])
    page_num += 1
    if page_num == 3:
        break
# 최신 정보만 의미가 있을 것 같음
# 30~50개 저장
# 더보기 -> 링크


# In[8]:


c


# In[9]:


n = 3
df_1 = [c[i*n : (i+1)*n] for i in range((len(c) + n - 1) // n )] 


# In[10]:


df_1[1]


# In[11]:


import pandas as pd


# In[12]:


df = pd.DataFrame.from_records(df_1,columns=('title','date','url'))


# In[13]:


df


# In[14]:


a.text, b.text, a['href']


# In[15]:


conn = sqlite3.connect('sonmin.db')
cur = conn.cursor()


# In[20]:


cur.executescript(''' 
    DROP TABLE IF EXISTS sonmin;
    CREATE TABLE sonmin(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    title TEXT  NOT NULL,
    date  TEXT   NOT NULL,
    url TEXT NOT NULL
    );
''')


# In[21]:


conn.commit()


# In[22]:


cur = conn.cursor()


# In[23]:


sql = "INSERT INTO sonmin(title, date, url) VALUES(?,?,?)"


# In[24]:


cur.executemany(sql, df_1)


# In[25]:


conn.commit()


# In[26]:


cur.close()


# In[23]:


conn = sqlite3.connect('sonmin.db')


# In[24]:


cur = conn.cursor()


# In[43]:


cur.execute("SELECT * FROM sonmin ORDER BY strftime('%Y-%m-%d', date)")
cur.fetchall()


# In[42]:


conn.commit()


# In[44]:


cur.close()


# In[ ]:




