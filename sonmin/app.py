from flask import Flask, render_template, request, Response
from flask_dropzone import Dropzone
import folium
from folium import plugins
import os
from sqlalchemy import create_engine
import sqlite3
import pandas as pd


# 업로드 파일 저장 경로 설정
basedir = os.path.abspath(os.path.dirname(__file__))
upload_dir = os.path.join(basedir, 'uploads')

app = Flask(__name__)
app.config['UPLOADED_PATH'] = upload_dir

dropzone = Dropzone(app)

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
    return render_template('index.html')

# 번역
@app.route('/translation', methods=['POST', 'GET'])
def translation():
    if request.method == 'POST':
        print(request.files.get('file'))

        f = request.files.get('file')
        f.save(os.path.join(upload_dir, f.filename))
        print(f.filename)

    return render_template('translation.html')

# 사전
@app.route('/dictionary')
def dictionary():
    return render_template('dictionary.html')

# 센터 정보
@app.route('/center_info')
def center_info():
    return render_template('center_info.html')

# 소개글
@app.route('/intro')
def introduce():
    return render_template('introduce.html')

# 앱 구동
if __name__ == '__main__':
    app.run()
