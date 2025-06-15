import numpy as np
from skimage.color import rgb2gray
from skimage.registration import optical_flow_horn_schunck, optical_flow_ilk

def flow_horn_schunck(img1: np.ndarray, img2: np.ndarray, alpha: float = 1.0, max_iter: int = 100) -> tuple:

    gray1 = rgb2gray(img1) if img1.ndim == 3 else img1
    gray2 = rgb2gray(img2) if img2.ndim == 3 else img2

    u, v = optical_flow_horn_schunck(gray1, gray2, video_alpha=alpha, niter=max_iter)
    return u, v


def flow_lucas_kanade(img1: np.ndarray, img2: np.ndarray, radius: int = 5, num_levels: int = 3) -> tuple:
    gray1 = rgb2gray(img1) if img1.ndim == 3 else img1
    gray2 = rgb2gray(img2) if img2.ndim == 3 else img2

    u, v = optical_flow_ilk(gray1, gray2,
                            radius=radius,
                            num_levels=num_levels)
    return u, v
