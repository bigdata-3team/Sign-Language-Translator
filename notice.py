# coding: utf-8

import requests
import time
import lxml
import sqlite3
import pandas as pd

from bs4 import BeautifulSoup
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, select, insert

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

dom.find_all('td', attrs={'class':"sFontDate"})

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

n = 3
df_1 = [c[i*n : (i+1)*n] for i in range((len(c) + n - 1) // n )] 

df = pd.DataFrame.from_records(df_1,columns=('title','date','url'))

conn = sqlite3.connect('sonmin.db')
cur = conn.cursor()

cur.executescript(''' 
    DROP TABLE IF EXISTS sonmin;
    CREATE TABLE sonmin(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    title TEXT  NOT NULL,
    date  TEXT   NOT NULL,
    url TEXT NOT NULL
    );
''')

conn.commit()
cur = conn.cursor()
sql = "INSERT INTO sonmin(title, date, url) VALUES(?,?,?)"
cur.executemany(sql, df_1)
conn.commit()
cur.close()

conn = sqlite3.connect('sonmin.db')
cur = conn.cursor()
cur.execute("SELECT * FROM sonmin ORDER BY strftime('%Y-%m-%d', date)")
cur.fetchall()
conn.commit()
cur.close()
