import os
from PIL import Image

import numpy as np

def zero_padding_4d(img_seq, max_len):
    """
    이미지 시퀸스들 앞에 0으로 된 이미지들 padding
    :param max_len: 이미지 시퀸스의 최종 길이
    """
    img_seq = img_seq.copy()
    img_shape = img_seq.shape[1:]
    img_augment_len = max_len - img_seq.shape[0]
    assert img_augment_len >=0, "max_len should longer than image sequence"
    if img_augment_len == 0:
        return img_seq
    img_zero = np.zeros((img_augment_len, *img_shape))
    img_seq = np.concatenate([img_zero, img_seq], axis = 0)
    return img_seq


def image_resize():
    pass


if __name__ == "__main__":
    target_folder = "C:/Users/Sudal_seok/Desktop/Sudal_python/MOV000235231_700X466"
    image_list = os.listdir(target_folder)
    image_seq = []
    for i in range(len(image_list)):
        image = Image.open(target_folder + "/{0}".format(image_list[i]))
        image = np.asarray(image)
        image = image.reshape(-1, *image.shape)
        image_seq.append(image)
    image_seq = np.concatenate(image_seq)
    print(image_seq.shape)
    image_seq = zero_padding_4d(image_seq, 10)
    print(image_seq.shape)
    print(image_seq[0].min(), image_seq[0].max())


