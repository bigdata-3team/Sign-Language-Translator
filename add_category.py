# coding: utf-8

import requests
import time
from bs4 import BeautifulSoup
import lxml
import re
from string import punctuation

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

params['pageIndex'] = 1
params['category'] = 'SPE001'
resp = requests.get(url, params=params)

dom = BeautifulSoup(resp.text, 'html.parser')

dom.prettify

s = dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[1].get('src')
s.replace('215X161.jpg', '700X466.mp4')

title = dom.select('#list > li > div > p > span.tit > a')[0].text
re.sub('[^가-힣]','',title)

dom.select('#list > li > div > p.s_dis > span > span')

s = dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[1].get('src')
re.findall('MOV.+',s)[0].replace('215X161.jpg', '700X466.mp4')

s = dom.select('#signListForm > div.result_list.mt_30 > div.wrap_list > ul > li > div.list_left > div > a > img')[1].get('src')
s = s.replace('215X161.jpg', '700X466.mp4')
re.findall('MOV.+',s)[0]


# 크롤링 시작
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

for category_num in range(9,12):
    try:
        params['category'] = 'SPE'+str(category_num).zfill(3)

        for pageIndex_num in range(155,157):
            params['pageIndex'] = pageIndex_num
            resp = requests.get(url, params=params)
            dom = BeautifulSoup(resp.text, 'html.parser')
            if len(dom.select('#list > li > div > p > span.tit > a')) == 0 :
                break
    except:
        # 페이지에 항목 없을 떄
        print('카테고리 끝')
        
category_num = 8
pageIndex_num = 132
while category_num < 15:
        try:
            params['category'] = 'SPE'+str(category_num).zfill(3)
            pageIndex_num = 132
            while pageIndex_num < 140:
                params['pageIndex'] = pageIndex_num
                resp = requests.get(url, params=params)
                dom = BeautifulSoup(resp.text, 'html.parser')
                if len(dom.select('#list > li > div > p > span.tit > a')) == 0 :
                    break
                pageIndex_num += 1
            category_num += 1
        except:
            print('카테고리 끝')
            break


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
