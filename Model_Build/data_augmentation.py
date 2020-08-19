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
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.imshow(img)


def plot_grid(imgs, nrows, ncols, figsize=(10, 10)):
    assert len(imgs) == nrows * ncols, f"Number of images should be {nrows} x {ncols}"
    _, axs = plt.subplots(nrows, ncols, figsize=figsize)
    axs = axs.flatten()
    for img, ax in zip(imgs, axs):
        show_img(img, ax)


def translate(img, shift=10, direction="right", roll=False):
    """
    이미지를 특정 방향으로 이동시키는 함수
    # 나는 shift 를 비율로 설정할거야.
    :param shift: float. 픽셀이 이동할 비율. 0과 1사이의 값
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
    음수인 랜덤 샘플을 많이 만들어낼수록 원본 이미지에 가까움
    # sample_code
    plot_grid([gaussian_noise(img, mean=0, sigma=0.03),
               gaussian_noise(img, mean=-1, sigma=0.03),
               gaussian_noise(img, mean=-2, sigma=0.03),
               gaussian_noise(img, mean=3, sigma=0.03),
               gaussian_noise(img, mean=0, sigma=0.03),
               gaussian_noise(img, mean=1, sigma=0.03),
               gaussian_noise(img, mean=0.5, sigma=0.03),
               gaussian_noise(img, mean=3, sigma=0.03)],
               2, 4, figsize=(30, 15))
    """
    img = img.copy()
    noise = np.random.normal(mean, sigma, img.shape)
    mask_overflow_upper = img+noise >= 1.0
    mask_overflow_lower = img+noise < 0
    noise[mask_overflow_upper] = (1.0 - img[mask_overflow_upper]) * 0.5
    noise[mask_overflow_lower] = 0
    img += noise
    return img


def change_channel_ratio(img, **kwargs):
    """
    이미지의 채널을 바꿔주는 함수
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

