#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import time
from bs4 import BeautifulSoup
import lxml
import re
from string import punctuation


# In[147]:


url = 'http://sldict.korean.go.kr/front/sign/signList.do'

params = {
    'current_pos_index': '',
    'origin_no': '0',
    'searchWay': '',
    'top_category': '',
    'category': 'SPE001',
    'detailCategory': '',
    'searchKeyword': '',
    'pageIndex': '1'
}


# In[148]:


params['pageIndex'] = 1
params['category'] = 'SPE001'
resp = requests.get(url, params=params)


# In[149]:


resp.status_code


# In[150]:


dom = BeautifulSoup(resp.text, 'html.parser')
len(dom.select('#list > li > div > p > span.tit > a'))


# In[151]:


dom = BeautifulSoup(resp.text, 'html.parser')


# In[45]:


dom.prettify


# In[46]:


dom.select('#menu > div > div > ul > li.on > ul > li > a > span')[0].text


# In[47]:


dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[1].get('src')


# In[48]:


s = dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[1].get('src')
s.replace('215X161.jpg', '700X466.mp4')


# In[49]:


dom.select('#list > li > div > p > span.tit > a')[0]


# In[50]:


title = dom.select('#list > li > div > p > span.tit > a')[0].text
re.sub('[^가-힣]','',title)


# In[51]:


dom.select('#list > li > div > p.s_dis > span > span')


# In[52]:


print( 
dom.select('#menu > div > div > ul > li.on > ul > li > a > span')[0].text,'\n',
dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[1].get('src').replace('215X161.jpg', '700X466.mp4'),'\n', 
re.sub('[^가-힣]','',dom.select('#list > li > div > p > span.tit > a')[0].text),'\n',
dom.select('#list > li > div > p.s_dis > span > span')[0].text
     )


# In[53]:


s = dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[1].get('src')
re.findall('MOV.+',s)[0].replace('215X161.jpg', '700X466.mp4')


# In[54]:


s = dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[1].get('src')
s = s.replace('215X161.jpg', '700X466.mp4')
re.findall('MOV.+',s)[0]


# ## 크롤링

# In[55]:


url = 'http://sldict.korean.go.kr/front/sign/signList.do'

params = {
    'current_pos_index': '',
    'origin_no': '0',
    'searchWay': '',
    'top_category': '',
    'category': 'SPE001',
    'detailCategory': '',
    'searchKeyword': '',
    'pageIndex': '1'
}

category_num = 1
pageIndex_num = 1


# In[56]:


for category_num in range(9,12):
    try:
        params['category'] = 'SPE'+str(category_num).zfill(3)
        print(params['category'],': ',dom.select('#menu > div > div > ul > li.on > ul > li > a > span')[category_num-1].text)
        for pageIndex_num in range(155,157):
            params['pageIndex'] = pageIndex_num
            print('pageIndex:',params['pageIndex'])
            resp = requests.get(url, params=params)
            print('code:',resp.status_code)
            dom = BeautifulSoup(resp.text, 'html.parser')
            print('len:',len(dom.select('#list > li > div > p > span.tit > a')),'\n')
            if len(dom.select('#list > li > div > p > span.tit > a')) == 0 :
                break
    except:
        print('카테고리 끝')


# In[91]:


category_num = 8
pageIndex_num = 132
while category_num < 15:
        try:
            params['category'] = 'SPE'+str(category_num).zfill(3)
            print(params['category'],': ',dom.select('#menu > div > div > ul > li.on > ul > li > a > span')[category_num-1].text)
            pageIndex_num = 132
            while pageIndex_num < 140:
                params['pageIndex'] = pageIndex_num
                print('pageIndex:',params['pageIndex'])
                resp = requests.get(url, params=params)
                print('code:',resp.status_code)
                dom = BeautifulSoup(resp.text, 'html.parser')
                print('len:',len(dom.select('#list > li > div > p > span.tit > a')),'\n')
                if len(dom.select('#list > li > div > p > span.tit > a')) == 0 :
                    break
                pageIndex_num += 1
            category_num += 1
        except:
            print('카테고리 끝')
            break


# In[106]:


category_num = 8
pageIndex_num = 132
while category_num < 15:
        try:
            params['category'] = 'SPE'+str(category_num).zfill(3)
            pageIndex_num = 132
            while pageIndex_num < 135:
                params['pageIndex'] = pageIndex_num
                resp = requests.get(url, params=params)
                dom = BeautifulSoup(resp.text, 'html.parser')
                dom.select('#menu > div > div > ul > li.on > ul > li > a > span')[category_num-1].text
                for i in range(len(dom.select('#list > li > div > p > span.tit > a'))):
                    print(dom.select('#menu > div > div > ul > li.on > ul > li > a > span')[category_num-1].text)
                    print(dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[2*i-1].get('src').replace('215X161.jpg', '700X466.mp4'),'\n', 
                          re.sub('[^가-힣]','',dom.select('#list > li > div > p > span.tit > a')[i].text),'\n',
                          dom.select('#list > li > div > p.s_dis > span > span')[i].text,'\n',
                          re.findall('MOV.+',dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[2*i-1].get('src').replace('215X161.jpg', '700X466.mp4'))[0],'\n')
                if len(dom.select('#list > li > div > p > span.tit > a')) == 0 :
                    print('페이지 끝 \n')
                    break
                pageIndex_num += 1
            category_num += 1
        except:
            print('카테고리 끝')
            break


# In[164]:


category_num = 1
pageIndex_num = 1
while True:
        try:
            params['category'] = 'SPE'+str(category_num).zfill(3)
            while True:
                params['pageIndex'] = pageIndex_num
                resp = requests.get(url, params=params)
                dom = BeautifulSoup(resp.text, 'html.parser')
                dom.select('#menu > div > div > ul > li.on > ul > li > a > span')[category_num-1].text
                for i in range(len(dom.select('#list > li > div > p > span.tit > a'))):
                    if len(re.findall('MOV.+',dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[2*i+1].get('src').replace('215X161.jpg', '700X466.mp4'))) == 0:
                        continue
                    f = open('add_category.txt','a')
                    f.write('\n'+dom.select('#menu > div > div > ul > li.on > ul > li > a > span')[category_num-1].text+
                           '\t'+dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[2*i+1].get('src').replace('215X161.jpg', '700X466.mp4')+
                            '\t'+re.sub('[^가-힣]','',dom.select('#list > li > div > p > span.tit > a')[i].text)+
                            '\t'+dom.select('#list > li > div > p.s_dis > span > span')[i].text+
                           '\t'+re.findall('MOV.+',dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[2*i+1].get('src').replace('215X161.jpg', '700X466.mp4'))[0])
                if len(dom.select('#list > li > div > p > span.tit > a')) == 0 :
                    print('페이지 끝 \n')
                    break
                pageIndex_num += 1
            category_num += 1
            pageIndex_num = 1
        except:
            print('카테고리 끝')
            f.close()
            break


# In[ ]:




