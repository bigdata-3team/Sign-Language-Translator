from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy, Pagination
from flask_admin import Admin
from flask_dropzone import Dropzone
from flask_paginate import Pagination, get_page_args
from konlpy.tag import Okt
from soynlp.hangle import compose, decompose

import tensorflow as tf
import pickle
import random
import os
import numpy as np
import cv2
import hgtk

okt = Okt()

# 업로드 파일 저장 경로 설정
basedir = os.path.abspath(os.path.dirname(__file__))

# sqlite 경로 생성해두기
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sonmin.sqlite"
app.config['SECRET_KEY'] = 'min'

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
    __tablename__ = "final_dictionary"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String, nullable=False)
    word = db.Column(db.String, nullable=False)
    mean = db.Column(db.String, nullable=False)
    src = db.Column(db.String, nullable=False)
    db.create_all()

# uploaded_video 테이블 클래스
class UploadedVideo(db.Model):
    __tablename__ = "uploaded_video"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    src = db.Column(db.String, nullable=False)
    db.create_all()


# 파일 업로드 공간 작동
app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'static/uploads'),
    # 저장 위치
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_TYPE='video',
    DROPZONE_MAX_FILE_SIZE=30,
    DROPZONE_MAX_FILES=1,
    DROPZONE_IN_FORM=True,
    DROPZONE_UPLOAD_ON_CLICK=True,
    DROPZONE_UPLOAD_ACTION='handle_upload',
    DROPZONE_UPLOAD_BTN_ID='submit',
)

# 프레임 추출 코드
def frame_extraction(file_path):
    max_len = 19;
    xlen = 120;
    ylen = 67
    cap = cv2.VideoCapture(file_path)
    count = 0
    img = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            count += 1
            if count % 9 == 0:
                frame = np.asarray(frame, dtype=np.float32)
                frame /= 255.0
                frame = cv2.resize(frame, dsize=(xlen, ylen))
                img.append(frame)
            k = cv2.waitKey(33)
            if k == 27:
                break
        else:
            break
    for i in range(len(img)):
        img[i] = img[i].reshape(-1, *img[i].shape)
    img = np.concatenate(img, axis=0)
    img_augment_len = max_len - img.shape[0]
    if img_augment_len == 0:
        return img.reshape(-1, *img.shape)
    elif img_augment_len > 0:
        img_zero = np.zeros((img_augment_len, *img.shape[1:]))
        img = np.concatenate([img_zero, img], axis=0)
        return img.reshape(-1, *img.shape)
    else:
        extra = img_augment_len * (-1)
        return img[extra:, ...].reshape(-1, *img.shape)




# 동사원형 추출하는 코드
class Lemmatizer:
    def __init__(self, stems, predefined=None):
        self._stems = stems
        self._predefined = {}
        if predefined:
            self._predefined.update(predefined)

    def is_stem(self, w):
        return w in self._stems

    def lemmatize(self, word):
        raise NotImplemented

    def candidates(self, word):
        candidates = set()
        for i in range(1, len(word) + 1):
            l = word[:i]
            r = word[i:]
            candidates.update(self._candidates(l, r))
        return candidates

    def _candidates(self, l, r):
        candidates = set()
        if self.is_stem(l):
            candidates.add((l, r))

        l_last = decompose(l[-1])
        l_last_ = compose(l_last[0], l_last[1], ' ')
        r_first = decompose(r[0]) if r else ('', '', '')
        r_first_ = compose(r_first[0], r_first[1], ' ') if r else ' '

        # ㄷ 불규칙 활용: 깨닫 + 아 -> 깨달아
        if l_last[2] == 'ㄹ' and r_first[0] == 'ㅇ':
            l_stem = l[:-1] + compose(l_last[0], l_last[1], 'ㄷ')
            if self.is_stem(l_stem):
                candidates.add((l_stem, r))

        # 르 불규칙 활용: 굴 + 러 -> 구르다
        if (l_last[2] == 'ㄹ') and (r_first_ == '러' or (r_first_ == '라')):
            l_stem = l[:-1] + compose(l_last[0], l_last[1], ' ') + '르'
            r_canon = compose('ㅇ', r_first[1], r_first[2]) + r[1:]
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        # ㅂ 불규칙 활용: 더러 + 워서 -> 더럽다
        if (l_last[2] == ' ') and (r_first_ == '워' or r_first_ == '와'):
            l_stem = l[:-1] + compose(l_last[0], l_last[1], 'ㅂ')
            r_canon = compose('ㅇ', 'ㅏ' if r_first_ == '와' else 'ㅓ', r_first[2]) + r[1:]
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        #         # 어미의 첫글자가 종성일 경우 (-ㄴ, -ㄹ, -ㅂ, -ㅅ)
        #         # 입 + 니다 -> 입니다
        if l_last[2] == 'ㄴ' or l_last[2] == 'ㄹ' or l_last[2] == 'ㅂ' or l_last[2] == 'ㅆ':
            l_stem = l[:-1] + compose(l_last[0], l_last[1], ' ')
            r_canon = l_last[2] + r
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        #         # ㅅ 불규칙 활용: 부 + 었다 -> 붓다
        #         # exception : 벗 + 어 -> 벗어
        if (l_last[2] == ' ' and l[-1] != '벗') and (r_first[0] == 'ㅇ'):
            l_stem = l[:-1] + compose(l_last[0], l_last[1], 'ㅅ')
            if self.is_stem(l_stem):
                candidates.add((l_stem, r))

        # 우 불규칙 활용: 똥퍼 + '' -> 똥푸다
        if l_last_ == '퍼':
            l_stem = l[:-1] + '푸'
            r_canon = compose('ㅇ', l_last[1], l_last[2]) + r
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        # 우 불규칙 활용: 줬 + 어 -> 주다
        if l_last[1] == 'ㅝ':
            l_stem = l[:-1] + compose(l_last[0], 'ㅜ', ' ')
            r_canon = compose('ㅇ', 'ㅓ', l_last[2]) + r
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        # 오 불규칙 활용: 왔 + 어 -> 오다
        if l_last[1] == 'ㅘ':
            l_stem = l[:-1] + compose(l_last[0], 'ㅗ', ' ')
            r_canon = compose('ㅇ', 'ㅏ', l_last[2]) + r
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        # ㅡ 탈락 불규칙 활용: 꺼 + '' -> 끄다 / 텄 + 어 -> 트다
        if (l_last[1] == 'ㅓ' or l_last[1] == 'ㅏ'):
            l_stem = l[:-1] + compose(l_last[0], 'ㅡ', ' ')
            r_canon = compose('ㅇ', l_last[1], l_last[2]) + r
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        # 거라, 너라 불규칙 활용
        # '-거라/-너라'를 어미로 취급하면 규칙 활용
        # if (l[-1] == '가') and (r and (r[0] == '라' or r[:2] == '거라')):
        #    # TODO

        # 러 불규칙 활용: 이르 + 러 -> 이르다
        # if (r_first[0] == 'ㄹ' and r_first[1] == 'ㅓ'):
        #     if self.is_stem(l):
        #         # TODO

        # 여 불규칙 활용
        # 하 + 였다 -> 하 + 았다 -> 하다: '였다'를 어미로 취급하면 규칙 활용

        # 여 불규칙 활용 (2)
        # 했 + 다 -> 하 + 았다 / 해 + 라니깐 -> 하 + 아라니깐 / 했 + 었다 -> 하 + 았었다
        if l_last[0] == 'ㅎ' and l_last[1] == 'ㅐ':
            l_stem = l[:-1] + '하'
            r_canon = compose('ㅇ', 'ㅏ', l_last[2]) + r
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        # ㅎ (탈락) 불규칙 활용
        # 파라 + 면 -> 파랗다
        if (l_last[2] == ' ' or l_last[2] == 'ㄴ' or l_last[2] == 'ㄹ' or l_last[2] == 'ㅂ' or l_last[2] == 'ㅆ'):
            l_stem = l[:-1] + compose(l_last[0], l_last[1], 'ㅎ')
            r_canon = r if l_last[2] == ' ' else l_last[2] + r
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        # ㅎ (축약) 불규칙 할용
        # 시퍼렜 + 다 -> 시퍼렇다, 파랬 + 다 -> 파랗다, 파래 + '' -> 파랗다
        if (l_last[1] == 'ㅐ') or (l_last[1] == 'ㅔ'):
            # exception : 그렇 + 아 -> 그래
            if len(l) >= 2 and l[-2] == '그' and l_last[0] == 'ㄹ':
                l_stem = l[:-1] + '렇'
            else:
                l_stem = l[:-1] + compose(l_last[0], 'ㅓ' if l_last[1] == 'ㅔ' else 'ㅏ', 'ㅎ')
            r_canon = compose('ㅇ', 'ㅓ' if l_last[1] == 'ㅔ' else 'ㅏ', l_last[2]) + r
            if self.is_stem(l_stem):
                candidates.add((l_stem, r_canon))

        ## Pre-defined set
        if (l, r) in self._predefined:
            for stem in self._predefined[(l, r)]:
                candidates.add(stem)

        return candidates

# 동사원형
stems = {
    '깨닫', '가',  # ㄷ 불규칙
    '구르', '들르',  # 르 불규칙
    '더럽', '곱', '감미롭',  # ㅂ 불규칙 (1)
    '이', '하', '푸르',  # # 어미의 첫글자가 종성일 경우
    '낫', '긋', '벗',  # ㅅ 불규칙
    '푸', '주', '누',  # 우 불규칙
    '오',  # 오 불규칙 (가제, 규칙 활용 ㅗ + ㅏ = ㅘ)
    '끄', '트',  # ㅡ 탈락 불규칙
    '파랗', '하얗', '그렇', '시퍼렇', '노랗',  # ㅎ (탈락) 불규칙
    '다하',  # 여 불규칙 활용 (2)
    '쉬', '먹', '뛰', '보', '만나',
}

lemmatizer = Lemmatizer(stems=stems)

# 문장입력 -> 단어 추출 코
def wordcraw(s):
    s = str(s)
    bfv = []
    word = []
    for i in okt.pos(s):
        if i not in [okt.pos(s)[_] for _ in range(len(okt.pos(s))) if
                     okt.pos(s)[_][1] == 'Josa' or okt.pos(s)[_][1] == 'Punctuation']:
            word.append(i)
    wordlist = [word[_][0] for _ in range(len(word))]
    verb_index = [_ for _ in range(len(word)) if word[_][1] == 'Verb']
    for i in range(len(verb_index)):
        if len(lemmatizer.candidates(word[verb_index[i]][0])) == 0:
            wordlist[verb_index[i]] = "set()"
            continue
        wordlist[verb_index[i]] = list(lemmatizer.candidates(word[verb_index[i]][0]))[0][0] + '다'
    return wordlist


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

# 모델 예측
def prediction_model(file_name):
    model_path = "./static/model/sonmin_model.h5"
    with tf.device("gpu:0"):
        train_model = tf.keras.models.load_model(model_path)
    img_input = frame_extraction("static/uploads/{0}".format(file_name))

    pred = train_model.predict(img_input)
    pred = np.argmax(pred)

    with open('./static/model/sonmin_word.p', 'rb') as file:
        idx_dict = pickle.load(file)

    for sign, idx in idx_dict.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if idx == pred:
            result = sign

    if not result:
        model_path = "./static/model/sonmin_model.h5"
        with tf.device("gpu:0"):
            train_model = tf.keras.models.load_model(model_path)
        img_input = frame_extraction("./uploads/{0}".format(file_name))

        pred = train_model.predict(img_input)
        pred = np.argmax(pred)

        with open('./static/model/sonmin_word.p', 'rb') as file:
            idx_dict = pickle.load(file)

        for sign, idx in idx_dict.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if idx == pred:
                result = sign


    return result



# ========== 번역 : 동영상 업로드 ==> 한국말 출력 ==========
@app.route('/translation')
def translate():
    return render_template('translation.html')


@app.route('/upload', methods=['POST'])
def handle_upload():
    for key, f in request.files.items():
        if key.startswith('file'):
            global result
            file_name = f.filename
            f.save(os.path.join(app.config['UPLOADED_PATH'], file_name))
            result = prediction_model(file_name=file_name)

            name = file_name
            src = 'static/uploads/{}'.format(file_name)

            video = UploadedVideo(name=name, src=src)
            db.session.add(video)
            db.session.commit()

    return result


@app.route('/translated', methods=['POST'])
def handle_form():
    path = 'static/uploads/'
    file_list = os.listdir(path)
    src = path + file_list[0]

    return render_template('translated.html', result=result, src=src)
# ========== 번역 : 동영상 업로드 ==> 한국말 출력 ==========

# ========== 번역 : 문장 입력 ==> 동영상 ==========
@app.route('/translation_word', methods=['GET', 'POST'])
def rtranslation():
    if request.method == 'POST':
        value = request.form['test']
        word_list = wordcraw(value)

        path = 'static/translate_video/'
        video_list = [(_[:-4], path + _) for _ in os.listdir(path)[:]]

        show_video = []
        for i in range(len(word_list)):
            if word_list[i] in [video_list[_][0] for _ in range(len(video_list))]:
                print(video_list[[video_list[_][0] for _ in range(len(video_list))].index(word_list[i])])
                show_video.append(video_list[[video_list[_][0] for _ in range(len(video_list))].index(word_list[i])])
            else:
                for j in range(len(word_list[i])):
                    print(hgtk.letter.decompose(word_list[i][j]))

                    for l in range(len(hgtk.letter.decompose(word_list[i][j]))):
                        nothing_word = list(hgtk.letter.decompose(word_list[i][j]))
                        if nothing_word[l] == '':
                            continue
                        print(video_list[[video_list[_][0] for _ in range(len(video_list))].index(
                            hgtk.letter.decompose(word_list[i][j])[l])])
                        show_video.append(video_list[[video_list[_][0] for _ in range(len(video_list))].index(
                            hgtk.letter.decompose(word_list[i][j])[l])])
        next_video = ["static/translate_video/" + show_video[_][0] + ".mp4" for _ in range(len(show_video))]

    return render_template('translated2.html', value=value, show_list=show_video, length=len(show_video), next_videos=next_video)
# ========== 번역 : 문장 입력 ==> 동영상 ==========

# ========== 사전 - 수어 영상 ==========
def get_videos(offset=0, per_page=10, videos=[]):
    return videos[offset: offset + per_page]

@app.route('/dictionary', methods=['POST', 'GET'])
def dictionary():
    if request.method == 'POST':
        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')
        category = request.form["category"]

        videos = DictionaryVideo.query.filter_by(category=category).all()
        total = len(videos)

        pagination_users = get_videos(offset=offset, per_page=per_page, videos=videos)
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    else:
        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')

        videos = DictionaryVideo.query.all()
        total = len(videos)
        pagination_users = get_videos(offset=offset, per_page=per_page, videos=videos)
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('dictionary.html',
                           videos=pagination_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination
                           )
# ========== 사전 - 수어 영상 ==========

# 센터 정보 -맵
@app.route('/map')
def map():
    # 맵 생성
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
def get_notice(offset=0, per_page=10):
    return notice[offset: offset + per_page]


# 센터 정보
@app.route('/center_info')
def center_info():
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page',
                                           )

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
    app.run(debug=True)
