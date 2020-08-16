import cv2
import os
import time

# 데이터셋이 저장된 폴더 확인
target_folder = "C://Users//shdhk//Desktop//team3"
file_list = os.listdir(target_folder + "//video")

for i in range(len(file_list)):
    # 동영상 파일명과 같은 폴더 생성
    new_folder = file_list[i][:-4]  # file_list에 있는 파일 이름은 확장자를 포함
    new_path = target_folder + "//{0}".format(new_folder)
    if not (os.path.isdir(new_path)):
        # 해당 파일명과 동일한 폴더가 없으면 생성
        os.mkdir(os.path.join(new_path))

    # 동영상 읽어서 원하는 부분 캡쳐(0.3초 간격 / 9 Frame)
    file_path = target_folder + "//video//" + file_list[i]
    cap = cv2.VideoCapture(file_path)
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()

        if ret:
            count += 1
            if count % 9 == 0:
                save_path = new_path + "//{0:02d}.png".format(count//9)
                cv2.imwrite(save_path, frame)
            k = cv2.waitKey(33)
            if k == 27:
                break
        else:
            break

    cap.release()
    if (i % 10) == 9 :
        time.sleep(5)


