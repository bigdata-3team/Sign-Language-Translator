# sign-language-translator(수어 번역기)
:office: &nbsp;&nbsp;빅데이터 캠퍼스 고려대학교 3팀

:man: &nbsp;&nbsp;박병근, 유성민, 이예지, 황효석

:calendar: &nbsp;&nbsp;20.08.06 ~ 20.08.31

:memo: &nbsp;&nbsp;수어 영상을 입력하면 그것이 의미하는 문장을 출력해주는 번역 시스템입니다. 
대부분의 일반인들은 수어를 알지 못합니다. 수어 번역기는, 일반인이 수어를 배우기 위한 시간과 비용을 들일 필요없이 손쉽게 농인들과 소통할 수 있는 장을 마련합니다.

## 1. 프로젝트 기획 배경

세계화는 우리의 일상이 되었습니다. 외국어를 배우는 것은 당연한 일이 되었고, 이를 도와줄 번역 시스템의 기술 또한 날로 발전하고 있습니다.

그러나 우리는 여기서 하나의 의문점을 발견합니다.



***"왜 사람들은 세계와 소통하려는 것 만큼 농인들과 소통하려 하지 않을까?"***



진정한 세계화는 모두가 함께 소통하는 것이라 생각합니다.

이 프로젝트를 통해 농인과 일반인의 원활한 의사소통을 기대합니다.



## 2. Sign-Language-Translator - 페이지 기능 소개

![no-img](./sonmin/static/images/main.png)

### (1) 시작화면 [ '***/***' ]

> "번역", "사전" 버튼을 통해 저희 사이트의 [번역], [사전] 페이지로 이동이 가능합니다.<br>
> "오늘의 수어 알아보기" 글자 누르기 또는, 스크롤을 통해 페이지의 하단으로 이동하면 방문할 때마다 무작위로 3가지 수어 영상을 보여드립니다.
>> - Github에 올릴 수 있는 파일 제한(1000개)으로 인해 "경제" 카테고리 동영상만 재생 가능합니다.

### (2) 번역화면 [ '***/translation***' ]

> 이 페이지에서는 탭 화면을 통해 (1)***수어를 한국어***로 또는 (2)***한국어를 수어***로 번역해줍니다.

====== 모델설명 =======

### (3) 사전화면 [ '***/dictionary***' ]

> 이 페이지에서는 "국립국어원" 페이지에서 크롤링 및 스크래핑 한 동영상을 보여드립니다.<br>
> [ sonmin.sqlite ]데이터베이스의 [ final_dictionary ]테이블에 있는 카테고리 칼럼 값으로 Pagination된 페이지를 보여줍니다.<br>
> 왼쪽에 있는 각 카테고리를 누르면 해당 카테고리의 동영상 목록을 보여줍니다.
>> - "국립국어원"과 "AIhub"에 연락한 결과, 저작권 문제로 "국립국어원"의 "전문용어" 카테고리만 보여드릴 수 있었습니다.
>> - "시작화면"의 "오늘의 수어 알아보기"의 같은 이슈로 인하여, "경제" 카테고리 동영상만 재생 가능합니다.

### (4) 센터정보 [ '***/center_info***' ]

> 이 페이지에서는 "한국농아인협회" 페이지의 공지사항을 보여드리고, 이와 함께 "한국농아인협회"와 관련된 "센터 지도"를 클러스터링을 통해 보여드립니다.<br>
> 공지사항의 "제목"을 클릭하면 "한국농아인협회"페이지의 링크를 새 창으로 띄워드립니다.<br>
> [ center_map ]테이블의 값들을, folium에 사용하여 페이지를 생성했습니다.
>> - "한국농아인협회" 페이지의 공지사항을 크롤링하여 [ sonmin.sqlite ]데이터베이스의 [ center_notice ]테이블에 저장하고, 이를 Pagination하여 보여드립니다.<br>
>> - "센터 지도"는 네이버 지도의 검색값 결과 중 [ "위도", "경도", "주소" ]값을 스크래핑하여 [ sonmin.sqlite ]데이터베이스의 [ center_map ]테이블에 저장했습니다.<br>

### (5) 소개글 [ '***/intro***' ]

> 이 페이지에서는 저희가 [ 프로젝트 주제를 선정하게 된 이유 ]와 [ 프로젝트 관련 영상 ], [ 키워드를 통한 Word Cloud ], 그리고 [ 팀원 정보 ]를 보여드립니다.

## 3. Introduce Database - sonmin.sqlite
[ center_map ] TABLE
```
index     : Integer
Name      : Text
Category  : Text
Longitude : Text
Latitue   : Text
Address   : Text
```

[ center_notice ] TABLE
```
id        : Integer
title     : Text, not null
date      : Text, not null
url       : Text, not null
```

[ final_dictionary ] TABLE : "dictionary_video", "restart_meaning" 테이블 JOIN
```
id        : Integer, not null
category  : String
word      : String
mean      : String
src       : String
```

## 4. requirements.txt
> 저희 프로젝트를 실행하기 위해 필요한 Python package 목록입니다.<br>
> requirements.txt는 [ git clone - ] 명령어 실행 후에 [ pip install -U -r requirements.txt ] 명령어를 실행시켜 주시면 됩니다.<br>
> 자세한 사용방법은 아래의 설명을  실행해 주세요.


## 5. 처음 사용하시는 분들께
> Pycharm과 같은 Python IDE의 터미널 환경 또는 Git-bash에서 실행해주세요.<br>
> 먼저, 다운로드 받고 싶은 폴더로 이동해주세요.<br>
> 이후에 다음의 명령어를 실행해주시면 됩니다.
```
$ git clone https://github.com/bigdata-3team/Sign-Language-Translator.git
$ pip install --upgrade pip
$ brew install gcc
$ pip install -U -r requirements.txt
```   


## 6. 연락처 - Contact
박병근 zordiac00@gmail.com

유성민 chelirt13@naver.com

이예지 yeji080808@gmail.com

황효석 hhseok960@gmail.com  
