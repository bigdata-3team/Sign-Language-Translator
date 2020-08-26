import numpy as np
from scipy.ndimage import rotate
import matplotlib.pyplot as plt
import cv2
import seaborn as sns
sns.set(color_codes=True)

"""
Reference order
1) Translate each image for several times.
2) Rotate each translation by 6 angels.
3) Put some gaussian noise on top.
"""

def show_img(img, ax):
    # 이미지 그려주는 함수
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.imshow(img)


def plot_grid(imgs, nrows, ncols, figsize=(10, 10)):
    """
    :param imgs: 그리려는 이미지들의 리스트
    :param nrows, ncols: subplot의 행과 열
    :return:
    """
    assert len(imgs) == nrows * ncols, f"Number of images should be {nrows} x {ncols}"
    _, axs = plt.subplots(nrows, ncols, figsize=figsize)
    axs = axs.flatten()
    for img, ax in zip(imgs, axs):
        show_img(img, ax)


def translate(img, shift=10, direction="right", roll=False):
    """
    이미지를 특정 방향으로 이동시키는 함수
    :param shift: int. 픽셀이 이동할 값
    :param direction: 픽셀이 이동할 방향.
    :param roll: 나머지 픽셀에 대한 처리
     - True : 이동하고 빈 픽셀을 원래의 이미지로 채워넣는 것
     - False : 이동하고 빈 픽셀을 이웃한 픽셀로 채워넣는 것
    """
    assert direction in ['right', 'left', 'down', 'up'], "Directions should be top|up|left|right"
    img = img.copy()
    if direction == 'right':
        right_slice = img[:, -shift:].copy()
        img[:, shift:] = img[:, :-shift]
        if roll:
            img[:,:shift] = np.fliplr(right_slice)
        else:
            temp = img[:, shift].reshape(img.shape[0], -1, 3)
            img[:,:shift] = np.tile(temp, (1, shift, 1))
    if direction == 'left':
        left_slice = img[:, :shift].copy()
        img[:, :-shift] = img[:, shift:]
        if roll:
            img[:, -shift:] = left_slice
        else:
            temp = img[:, -(shift + 1)].reshape(img.shape[0], -1, 3)
            img[:, -shift:] = np.tile(temp, (1, shift, 1))
    if direction == 'down':
        down_slice = img[-shift:, :].copy()
        img[shift:, :] = img[:-shift,:]
        if roll:
            img[:shift, :] = down_slice
        else:
            temp = img[shift, :].reshape(-1, img.shape[1], 3)
            img[:shift, :] = np.tile(temp, (shift, 1, 1))
    if direction == 'up':
        upper_slice = img[:shift, :].copy()
        img[:-shift, :] = img[shift:, :]
        if roll:
            img[-shift:,:] = upper_slice
        else:
            temp = img[-(shift+1), :].reshape(-1, img.shape[1], 3)
            img[-shift:,:] = np.tile(temp, (shift, 1, 1))
    return img


def rotate_img(img, angle, bg_patch = (10, 10)):
    """
    이미지를 회전하는 함수. 회전 후 나머지 부분은 가장자리 값의 평균으로 채워넣음
    우리 프로젝트에서는 각도가 [-20, 20] 사이에 있도록
    :param img:
    :param angle:
    :param bg_patch:
    """
    img = img.copy()
    rgb = len(img.shape) == 3
    if rgb:
        bg_color = np.mean(img[:bg_patch[0], :bg_patch[1], :], axis=(0,1))
    else:
        bg_color = np.mean(img[:bg_patch[0], :bg_patch[1]])
    img = rotate(img, angle, reshape=False)
    mask = [img <= 0, np.any(img <= 0, axis=-1)][rgb]
    img[mask] = bg_color
    return img


def gaussian_noise(img, mean=0, sigma=0.03):
    """
    모든 이미지에 같은 노이즈를 적용. zero-padding에는 노이즈가 들어가면 안됨
    음수인 랜덤 샘플을 많이 만들어낼수록 원본 이미지에 가까움
    # sample_code
    gaussian_noise(img, mean=0, sigma=0.03),
    gaussian_noise(img, mean=-1, sigma=0.03),
    """
    img = img.copy()
    start = 0
    # zero-padding 이미지 수를 탐색
    for i in range(img.shape[0]):
        if img[i].sum() == 0:
            continue
        else:
            start = i
            break
    # 하나의 이미지 크기에 해당하는 노이즈 생성
    noise = np.random.normal(mean, sigma, img.shape[1:])
    # 노이즈를 필요한 만큼 복제
    noise = np.repeat(noise[np.newaxis, ...], img.shape[0] - start, axis=0)
    # 이미지 각 픽셀의 값은 0과 1사이에 있으므로 노이즈를 더해도 이 범위 안에 있게 노이즈를 조절
    mask_overflow_upper = img[start:, ...]+noise >= 1.0
    mask_overflow_lower = img[start:, ...]+noise < 0
    noise[mask_overflow_upper] = (1.0 - img[start:,...][mask_overflow_upper]) * 0.5
    noise[mask_overflow_lower] = 0
    img[start:, ...] += noise
    return img


def change_channel_ratio(img, **kwargs):
    """
    이미지에서 원하는 채널은 원하는 비율만큼 조절하는 함수
    # sample_code
    change_channel_ratio(img, r=0.3),
    change_channel_ratio(img, r=0.3, b=0.3),
    change_channel_ratio(img, r=0.3, g=0.3, b=0.3)
    """
    img = img.copy()
    for color, ratio in kwargs.items():
        assert color in ['r', 'g', 'b'], "Color should be r|g|b"
        assert ratio <= 1, "Ratio should be less than 1."
        ci = 'rgb'.index(color)
        print(color, ratio)
        img[:, :, ci] *= ratio
    return img


def clipped_zoom(img, zoom_factor, **kwargs):
    """
    :param zoom_factor: float. 주어진 비율만큼 이미지를 확대해준다.
    :param kwargs:
    """
    # assert zoom_factor >= 1, "zoom_factor should be more than 1."
    img = img.copy()
    # zoom을 적용하는 것은 RGB 채널 이외의 배열
    h, w = img.shape[:2]
    new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
    y1, x1 = max(0, new_h - h) // 2, max(0, new_w - w) // 2
    y2, x2 = y1 + h, x1 + w
    bbox = np.array([y1, x1, y2, x2])
    # 다시 원래 배열의 좌표로 변환
    bbox = (bbox / zoom_factor).astype(np.int)
    y1, x1, y2, x2 = bbox
    cropped_img = img[y1:y2, x1:x2]

    # Handle padding when downscaling
    resize_h, resize_w = min(new_h, h), min(new_w, w)
    pad_h1, pad_w1 = (h - resize_h) // 2, (w - resize_w) // 2
    pad_h2, pad_w2 = (h - resize_h) - pad_h1, (w - resize_w) - pad_w1
    pad_spec = [(pad_h1, pad_h2), (pad_w1, pad_w2)] + [(0, 0)] * (img.ndim - 2)

    img = cv2.resize(cropped_img, (w, h))
    img = np.pad(img, pad_spec, mode='edge')
    return img


def apply_data_augmentation (img_seq, process):
    """
    :param process: 처리할 항목 리스트 - 1: translate / 2: rotate / 3: gaussian / 4: channel ratio / 5: zoom
    처리할 항목을 받으면 순차적으로 이미지에 변형본 적용
    :return:
    """
    img_seq = img_seq.copy()
    for type in process:
        if type == 1: # Translation
            for i in range(img_seq.shape[0]):
                # 방향과 이동할 픽셀 값을 랜덤값으로 전달 받아서 각 데이터에 적용
                temp = img_seq[i]
                direction = np.random.choice(["right", "left", "down", "up"], size=1)[0]
                shift = np.random.randint(10, 20, size=1)[0]
                for j in range(temp.shape[0]):
                    temp[j] = translate(temp[j], shift=shift, direction=direction)
                img_seq[i] = temp

        elif type == 2: # Rotate
            for i in range(img_seq.shape[0]):
                # 이미지를 회전시킬 정도를 랜덤값으로 전달 받아서 각 데이터에 적용
                temp = img_seq[i]
                angle = np.random.randint(-20, 21, size=1)[0]
                for j in range(temp.shape[0]):
                    temp[j] = rotate_img(temp[j], angle=angle)
                img_seq[i] = temp

        elif type == 3: # Gaussian Noise
            for i in range(img_seq.shape[0]):
                # 노이즈를 생성할 가우시안 분포의 파라미터를 랜덤값으로 받아서 각 데이터에 적용
                mean = np.random.uniform(0, 0.5, size=1)[0]
                std = np.random.uniform(0.01, 0.1, size=1)[0]
                img_seq[i] = gaussian_noise(img_seq[i], mean=mean, sigma=std)

        elif type == 4: # Channel Ratio
            for i in range(img_seq.shape[0]):
                # 변경할 채널과 비율을 랜덤값으로 전달 받아서 각 데이터에 적용
                temp = img_seq[i]
                color = np.random.choice(["r", "g", "b"], size=1, replace=False)[0]
                ratio = np.random.uniform(0, 1, size=1)[0]
                for j in range(temp.shape[0]):
                    if color == "r":
                        temp[j] = change_channel_ratio(temp[j], r=ratio)
                    elif color == "g":
                        temp[j] = change_channel_ratio(temp[j], g=ratio)
                    else:
                        temp[j] = change_channel_ratio(temp[j], b=ratio)
                img_seq[i] = temp

        elif type == 5: # Zoom
            for i in range(img_seq.shape[0]):
                # 이미지를 확대시킬 비율을 랜덤값으로 전달 받아서 각 데이터에 적용
                temp = img_seq[i]
                ratio = np.random.uniform(1.0, 1.5, size=1)[0]
                for j in range(temp.shape[0]):
                    temp[j] = clipped_zoom(temp[j], zoom_factor=ratio)
                img_seq[i] = temp
    return img_seq


if __name__ == "__main__":
    test_img = np.asarray(plt.imread("07.png"))
    plt.figure(figsize=(5, 5), dpi=100)
    sns.distplot(test_img[:, :, 0].flatten(), color='maroon')
    sns.distplot(test_img[:, :, 1].flatten(), color='green')
    sns.distplot(test_img[:, :, 2].flatten(), color='blue').set_title("RGB Distribution")
    plt.show()

    plot_grid([clipped_zoom(test_img, zoom_factor=1),
               clipped_zoom(test_img, zoom_factor=1.3),
               clipped_zoom(test_img, zoom_factor=2),
               clipped_zoom(test_img, zoom_factor=5),
               clipped_zoom(test_img, zoom_factor=0.9),
               clipped_zoom(test_img, zoom_factor=0.8),
               clipped_zoom(test_img, zoom_factor=0.5),
               clipped_zoom(test_img, zoom_factor=0.1)],
              2, 4, figsize=(30, 15))
    plt.tight_layout()
    plt.show()

