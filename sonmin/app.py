from flask import Flask, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy, Pagination
from flask_admin import Admin
from flask_dropzone import Dropzone
from flask_paginate import Pagination, get_page_args
from folium.plugins import MarkerCluster
from folium import plugins
from sqlalchemy import create_engine

import random
import folium
import os
import sqlite3
import pandas as pd



# 업로드 파일 저장 경로 설정
basedir = os.path.abspath(os.path.dirname(__file__))
upload_dir = os.path.join(basedir, 'uploads')


# sqlite 경로 생성해두기
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sonmin.sqlite"
app.config['SECRET_KEY'] = 'min'
app.config['UPLOADED_PATH'] = upload_dir


# db, admin, dropzone 객체 생성
db = SQLAlchemy(app)
admin = Admin(name='yeji')
admin.init_app(app)
dropzone = Dropzone(app)


# center_map 테이블 클래스
class CenterMap(db.Model):
    __tablename__ = "center_map"
    index = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String, nullable=False)
    Category = db.Column(db.String, nullable=False)
    Longitude = db.Column(db.String, nullable=False)
    Latitude = db.Column(db.String, nullable=False)
    Address = db.Column(db.String, nullable=False)
db.create_all()


# center_notice 테이블 클래스
class CenterNotice(db.Model):
    __tablename__ = "center_notice"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
db.create_all()


# dictionary_video 테이블 클래스
class DictionaryVideo(db.Model):
    __tablename__ = "dictionary_video"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String, nullable=False)
    mean = db.Column(db.String, nullable=False)
    src = db.Column(db.String, nullable=False)
db.create_all()


# 파일 업로드 공간 작동
app.config.update(
    UPLOADED_PATH=upload_dir,
    # 저장 위치
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_TYPE='video',
    DROPZONE_MAX_FILE_SIZE=3,
    DROPZONE_MAX_FILES=10,
)


# 메인
@app.route('/')
def main():
    # 디비 값 INSERT
    # path = "../sonmin/static/videos"
    # file_list = os.listdir(path)
    # for file_name in file_list:
    #     video = DictionaryVideo(mean=file_name.split("_")[-1],
    #                             category=file_name.split("_")[0],
    #                             src=path+"/"+file_name)
    #     db.session.add(video)
    #     db.session.commit()

    # src 값 UPDATE
    # video = DictionaryVideo.query.all()
    # for i in range(DictionaryVideo.query.count()):
    #     video[i].src = video[i].src.split("n/")[-1]
    # db.session.commit()

    video_cnt = DictionaryVideo.query.count()  # 비디오 데이터 개수
    ran_num = random.randint(0, int(video_cnt))  # 랜덤 id 값
    ran_list = []  # 랜덤 id 값 넣을 list
    video_list = []  # 랜덤 id 값 넣을 list

    for i in range(3):
        while ran_num in ran_list:
            ran_num = random.randint(0, int(video_cnt))
        video = DictionaryVideo.query.get(ran_num)
        video_list.append(video)
        ran_list.append(ran_num)

    return render_template('index.html', list=video_list)


# 번역
@app.route('/translation', methods=['POST', 'GET'])
def translation():
    if request.method == 'POST':
        print(request.files.get('file'))

        f = request.files.get('file')
        f.save(os.path.join(upload_dir, f.filename))
        print(f.filename)

    return render_template('translation.html')


# 수어 영상
videos = DictionaryVideo.query.all()
def get_videos(offset=0, per_page=10):
    return videos[offset: offset + per_page]


# 사전
@app.route('/dictionary')
def dictionary():
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(videos)
    pagination_users = get_videos(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    print(pagination_users)
    return render_template('dictionary.html',
                           videos=pagination_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination
                           )


# # 센터 정보 -맵
@app.route('/map')
def map():
    # m = folium.Map([36.0, 127.5], zoom_start=6, min_zoom=5, width=360, height=500)
    # marker_cluster = MarkerCluster().add_to(m)
    # map = CenterMap.query.all()
    #
    # for i in range(len(map)):
    #     folium.Marker(
    #         location=[float(map[i].Latitude), float(map[i].Longitude)],
    #         popup=map[i].Name,
    #     ).add_to(marker_cluster)
    #
    # return m._repr_html_()
    return render_template('map.html')


# 센터 정보 -공지사항
notice = CenterNotice.query.all()
def get_notice(offset=0, per_page=8):
    return notice[offset: offset + per_page]


# 센터 정보
@app.route('/center_info')
def center_info():

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page',
                                           )
    per_page = 8
    offset = 8*(page-1) + 1
    total = len(notice)
    pagination_users = get_notice(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('center_info.html',
                           users=pagination_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination
                           )


# 소개글
@app.route('/intro')
def introduce():
    return render_template('introduce.html')

# 앱 구동
if __name__ == '__main__':
    app.run()
