#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
from selenium import webdriver
import urllib.request
import re
from string import punctuation
import pandas as pd
import csv


# In[31]:


driver = webdriver.Chrome('/Users/SeongMin/chromedriver.exe')


# In[39]:


i = 1
j = 1
category_list = ['CTE','SPE']
category = category_list[j]

file = open('수어.csv','a',newline="")

while True:
    page = str(i)
    print("i",page) # 확인
    url = 'http://sldict.korean.go.kr/front/sign/signList.do?current_pos_index=&origin_no=0&searchWay=&top_category='+category+'&category=&detailCategory=&searchKeyword=&pageIndex='+page+'&pageJumpIndex='
    driver.get(url)
    num_content = driver.find_elements_by_xpath('//*[@id="list"]/li/div/p[1]/span[1]/a')
    view_list = driver.find_elements_by_xpath('//*[@id="list"]/li/div/p[2]/span/span')
    view = [view_list[_].text for _ in range(len(num_content))]

    print(len(num_content)) # 확인
    time.sleep(1)
    
    if len(num_content) == 0:
        j += 1
        if j == 2:
            f.close()
            break
        category = category_list[j]
        i = 1
        continue
    
    for k in range(len(num_content)):
        print("k",k) # 확인
        driver.find_elements_by_xpath('//*[@id="list"]/li/div/p[1]/span[1]/a')[k].click()
        time.sleep(1)
        
        try:
            down_url = driver.find_element_by_xpath('//*[@id="html5Video"]/source[2]').get_attribute('src')
            title = driver.find_element_by_xpath('//*[@id="signViewForm"]/dl/dd[1]').text
            title = re.sub('[^가-힣]','',title)
            end_title = down_url.split('/')[-1]
            views = view[k]
            f = open('수어.txt','a')
            f.write('\n'+down_url+'\t'+title+'\t'+end_title+'\t'+views)

            wr = csv.writer(file)
            wr.writerow([down_url,title,end_title,views])

            time.sleep(1)
            print(down_url, title, views)    
            
        except:
            print('Error:page=',i,' ',k,'번째')      
        driver.back()
            
    i += 1


# In[41]:


file.close()


# In[6]:


# 일상용어
# 32페이지 7번째 오류
# 203페이지 8번째
# 272페이지 9번째
# 405페이지 5번째
# 710페이지 0번째
# 782페이지 9번째

# 전문용어
# 114페이지 4번째 오류
# 290페이지 9번째
# 1009페이지 0번째
# 1025페이지 3번째


# In[ ]:




