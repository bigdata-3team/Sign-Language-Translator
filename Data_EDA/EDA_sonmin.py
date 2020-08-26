import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

target_folder = "C://Users//shdhk//Desktop//team3_selected"
folder_list = os.listdir(target_folder)

"""
각 이미지 시계열에서 확인할 자료들
file_name: 이미지 파일 이름
seq_len: 이미지 시계열 길이
img_row: 이미지 가로 길이
img_col: 이미지 세로 길이
RGB: 이미지에서 RGB 채널 각각의 최대, 최소, 중앙값, 평균, 표준편차
"""
df_EDA = pd.DataFrame(columns=["file_name", "seq_len", "img_row", "img_col",
                               "R_min", "R_median", "R_max", "G_min", "G_median", "G_max",
                               "B_min", "B_median", "B_max", "R_mean", "R_std", "G_mean",
                               "G_std", "B_mean", "B_std"
                               ])

for i in range(len(folder_list)):
    new_row = [folder_list[i]]
    img_path = target_folder + "//{0}".format(folder_list[i])
    img_list = os.listdir(img_path)
    new_row.append(len(img_list))
    test_img = np.asarray(plt.imread(img_path + "//{0}".format(img_list[0])))
    new_row += [test_img.shape[0], test_img.shape[1]]
    r_seq = test_img[:, :, 0].flatten()
    g_seq = test_img[:, :, 1].flatten()
    b_seq = test_img[:, :, 2].flatten()
    if i % 1000 == 0:
        # 1000개 단위로 이미지의 RGB 채널 분포를 그리는 코드
        plt.figure(figsize=(15, 15))
        sns.distplot(r_seq, color='maroon')
        sns.distplot(g_seq, color='green')
        sns.distplot(b_seq, color='blue').set_title("RGB Distribution")
        # plt.tight_layout()
        plt.savefig("{0}_RGBdistplot.png".format(folder_list[i]), dpi = 400)
        plt.close()
    color = [np.min(r_seq), np.median(r_seq), np.max(r_seq),
             np.min(g_seq), np.median(g_seq), np.max(g_seq),
             np.min(b_seq), np.median(b_seq), np.max(b_seq),
             np.mean(r_seq), np.std(r_seq), np.mean(g_seq),
             np.std(g_seq), np.mean(b_seq), np.std(b_seq)]
    # 얻은 정보를 데이터프레임에 추가
    df_EDA.loc[i] = new_row + color

dataset_annotation = pd.read_excel("수어_데이터셋_어노테이션.xlsx")
dataset_annotation["file_name"] = dataset_annotation["파일명"].str[:-4]
dataset_annotation = dataset_annotation[["file_name", "한국어"]]
# 데이터셋 어노테이션 파일에서 해당 이미지 시계열이 나타내는 한국어를 가져옴
df_EDA = pd.merge(df_EDA, dataset_annotation, how="outer", on="file_name")

df_EDA.to_excel("EDA.xlsx", header=True, index=False)