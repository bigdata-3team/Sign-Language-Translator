import os
import numpy as np
import pandas as pd
from pandas import DataFrame
from PIL import Image

# dataset prepare
target_folder = "C://Users//shdhk//Desktop//team3_selected"
folder_list = os.listdir(target_folder)

dataset_annotation = pd.read_excel("수어_데이터셋_어노테이션.xlsx")
dataset_annotation["folder_name"] = dataset_annotation["파일명"].str[:-4]

input_data = []
output_data = []
# for i in range(len(folder_list)):
for i in range(3):
    image_path = target_folder + "//{0}".format(folder_list[i])
    image_list = os.listdir(image_path)
    print(image_list)
    """
    나중에 굳이 추가를 할 필요가 있을까 싶은... sorting을 해야할까?
    """
    img_seq = []
    for j in range(len(image_list)):
        image = Image.open(image_path + "//{0}".format(image_list[j]))
        image = np.asarray(image)
        image = image.reshape(-1, *image.shape)
        img_seq.append(image)
    img_seq = np.concatenate(img_seq)
    img_seq = img_seq.reshape(-1, *img_seq.shape)
    input_data.append(img_seq)
    label = dataset_annotation[dataset_annotation["folder_name"] == folder_list[i]].loc[:, "한국어"].values[0]
    if type(label) == int:
        label = str(label)
    output_data.append(label)
