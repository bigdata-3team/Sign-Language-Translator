import os
import numpy as np
import pandas as pd
from PIL import Image
import cv2
import data_reshape as dr


def read_ai (xlen = 1280, ylen = 720):
    # dataset prepare
    target_folder = "C://Users//shdhk//Desktop//team3_selected"
    folder_list = os.listdir(target_folder)

    dataset_annotation = pd.read_excel("수어_데이터셋_어노테이션.xlsx")
    dataset_annotation["folder_name"] = dataset_annotation["파일명"].str[:-4]

    input_data = []
    output_data = []
    img_max_len = 0
    # for i in range(500):
    for i in range(len(folder_list)):
        img_path = target_folder + "//{0}".format(folder_list[i])
        img_list = os.listdir(img_path)
        img_list.sort()
        if len(img_list) > img_max_len:
            img_max_len = len(img_list)
        # print(img_max_len)
        img_seq = []
        for j in range(len(img_list)):
            image = Image.open(img_path + "//{0}".format(img_list[j]))
            image = np.asarray(image)
            image = cv2.resize(image, dsize=(xlen, ylen))
            image = image.reshape(-1, *image.shape)
            img_seq.append(image)
        img_seq = np.concatenate(img_seq)
        # img_seq = img_seq.reshape(-1, *img_seq.shape)
        input_data.append(img_seq)
        print("Read {0} Complete".format(i))
        label = dataset_annotation[dataset_annotation["folder_name"] == folder_list[i]].loc[:, "한국어"].values[0]
        if type(label) == int:
            label = str(label)
        output_data.append(label)

    for i in range(len(input_data)):
        # print("Before: ", input_data[i].shape)
        input_data[i] = dr.zero_padding_4d(input_data[i], img_max_len)
        # print("After: ", input_data[i].shape)

    return input_data, output_data, img_max_len