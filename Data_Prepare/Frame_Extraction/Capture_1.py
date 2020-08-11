import cv2
import os
import time

# 데이터셋이 저장된 폴더 확인
target_folder = "C://Users//shdhk//Desktop//team3_1"
folder_list = os.listdir(target_folder)
for i in range(len(folder_list)):
    new_folder = "Extracted_" + folder_list[i]
    new_path = target_folder + "//{0}".format(new_folder)
    if not (os.path.isdir(new_path)):
        # 해당 파일명과 동일한 폴더가 없으면 생성
        os.mkdir(os.path.join(new_path))

    file_list = os.listdir(target_folder + "//{0}".format(folder_list[i]))
    for j in range(len(file_list)):
        new_path2 = new_path + "//{0}".format(file_list[j][:-4])
        if not (os.path.isdir(new_path2)):
            os.mkdir(os.path.join(new_path2))

        # 동영상 읽어서 원하는 부분 캡쳐(0.3초 간격 / 9 Frame)
        file_path = target_folder + "//{0}//".format(folder_list[i]) + file_list[j]
        cap = cv2.VideoCapture(file_path)
        # restrict = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * 3 / 7) + 1
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                count += 1
                if count % 9 == 0:
                    save_path = new_path2 + "//{0:02d}.png".format(count // 9)
                    cv2.imwrite(save_path, frame)
                k = cv2.waitKey(33)
                if k == 27:
                    break
            else:
                break

        cap.release()
        if (i % 10) == 9:
            time.sleep(5)