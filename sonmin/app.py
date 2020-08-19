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


# 테스트(성민)
@app.route('/test')
def test():
    return render_template('test.html')


# db 테스트
conn = sqlite3.connect('C:/Users/SeongMin/naver_map.db')
c = conn.cursor()

sql = """
SELECT *
FROM naver_map
"""


table = pd.read_sql(sql, conn)
data = table[['Latitude','Longitude']]
data["Latitude"] = pd.to_numeric((data["Latitude"]))
data["Longitude"] = pd.to_numeric((data["Longitude"]))

conn.close()


# 맵
@app.route('/map')
def test2():
    global data

    for i in range(data.shape[0]):
        point = list(data.iloc[i, :])
        m = folium.Map(point, zoom_start=10, min_zoom=7)
        # folium.Marker(m, popup='maptest6', tooltip='test6').add_to(m)
    pop_up_list = list(range(data.shape[0]))
    pop_up_list = list(map(str, pop_up_list))
    plugins.MarkerCluster(data, popups=pop_up_list).add_to(m)
    return m._repr_html_()


# 맵 테스트
@app.route('/test2')
def test3():
    return render_template('test2.html')




# device_installtions = pd.read_sql(device_installtions_query, mariadb_connection)
#
# # Live DataBase에서는 없애도 될 문장
# device_installtions = device_installtions[pd.notnull(device_installtions["carId"])]
#
# device_installtions["carId"] = device_installtions["carId"].astype(int)
# device_installtions

# 앱 구동
if __name__ == '__main__':
    app.run()
