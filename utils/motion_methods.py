import numpy as np
import cv2
from scipy.signal import convolve2d
from typing import Tuple

# Try to import scikit-image optical flow functions (may not be available in all versions)
try:
    from skimage.color import rgb2gray
    from skimage.registration import optical_flow_horn_schunck, optical_flow_ilk
    SKIMAGE_FLOW_AVAILABLE = True
except ImportError:
    print("Warning: Scikit-image optical flow functions not available in this version")
    SKIMAGE_FLOW_AVAILABLE = False

    def rgb2gray(image):
        """Fallback RGB to grayscale conversion."""
        if len(image.shape) == 3:
            return np.dot(image[..., :3], [0.2989, 0.5870, 0.1140])
        return image

# Self-made implementations


def horn_schunck_custom(im1: np.ndarray, im2: np.ndarray, alpha: float = 1.0, num_iter: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """Custom implementation of Horn-Schunck optical flow."""
    im1 = im1.astype(np.float32)
    im2 = im2.astype(np.float32)

    kernel_x = np.array([[-1, 1], [-1, 1]]) * 0.25
    kernel_y = np.array([[-1, -1], [1, 1]]) * 0.25
    kernel_t = np.ones((2, 2)) * 0.25

    Ix = convolve2d(im1, kernel_x, boundary='symm', mode='same') + \
        convolve2d(im2, kernel_x, boundary='symm', mode='same')
    Iy = convolve2d(im1, kernel_y, boundary='symm', mode='same') + \
        convolve2d(im2, kernel_y, boundary='symm', mode='same')
    It = convolve2d(im2, kernel_t, boundary='symm', mode='same') - \
        convolve2d(im1, kernel_t, boundary='symm', mode='same')

    u = np.zeros_like(im1)
    v = np.zeros_like(im1)

    kernel_avg = np.array([
        [0, 0.25, 0],
        [0.25, 0, 0.25],
        [0, 0.25, 0]]
    )

    for _ in range(num_iter):
        u_avg = convolve2d(u, kernel_avg, boundary='symm', mode='same')
        v_avg = convolve2d(v, kernel_avg, boundary='symm', mode='same')
        numerator = (Ix * u_avg + Iy * v_avg + It)
        denominator = (alpha**2 + Ix**2 + Iy**2)
        term = numerator / denominator
        u = u_avg - Ix * term
        v = v_avg - Iy * term
    return u, v


def lucas_kanade_dense_custom(im1: np.ndarray, im2: np.ndarray, window_size: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """Custom dense Lucas-Kanade implementation."""
    im1 = im1.astype(np.float32)
    im2 = im2.astype(np.float32)

    Ix = cv2.Sobel(im1, cv2.CV_32F, 1, 0, ksize=3) + \
        cv2.Sobel(im2, cv2.CV_32F, 1, 0, ksize=3)
    Iy = cv2.Sobel(im1, cv2.CV_32F, 0, 1, ksize=3) + \
        cv2.Sobel(im2, cv2.CV_32F, 0, 1, ksize=3)
    It = im2 - im1

    half_w = window_size // 2
    u = np.zeros(im1.shape, dtype=np.float32)
    v = np.zeros(im1.shape, dtype=np.float32)

    h, w = im1.shape
    for y in range(half_w, h - half_w):
        for x in range(half_w, w - half_w):
            Ix_win = Ix[y-half_w:y+half_w+1, x-half_w:x+half_w+1].flatten()
            Iy_win = Iy[y-half_w:y+half_w+1, x-half_w:x+half_w+1].flatten()
            It_win = It[y-half_w:y+half_w+1, x-half_w:x+half_w+1].flatten()

            A = np.stack((Ix_win, Iy_win), axis=1)
            b = -It_win.reshape(-1, 1)

            nu, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
            u[y, x] = nu[0]
            v[y, x] = nu[1]

    return u, v


def pyr_lucas_kanade_custom(im1: np.ndarray, im2: np.ndarray, num_levels: int = 3, window_size: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """Custom pyramidal Lucas-Kanade implementation."""
    pyr1 = [im1]
    pyr2 = [im2]
    for _ in range(1, num_levels):
        pyr1.append(cv2.pyrDown(pyr1[-1]))
        pyr2.append(cv2.pyrDown(pyr2[-1]))

    h_coarse, w_coarse = pyr1[-1].shape
    u = np.zeros((h_coarse, w_coarse), dtype=np.float32)
    v = np.zeros((h_coarse, w_coarse), dtype=np.float32)

    for lvl in reversed(range(num_levels)):
        if lvl < num_levels - 1:
            u = cv2.pyrUp(u) * 2
            v = cv2.pyrUp(v) * 2
            u = cv2.resize(u, (pyr1[lvl].shape[1], pyr1[lvl].shape[0]))
            v = cv2.resize(v, (pyr1[lvl].shape[1], pyr1[lvl].shape[0]))

        h, w = pyr1[lvl].shape
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
        map_x = (grid_x + u).astype(np.float32)
        map_y = (grid_y + v).astype(np.float32)
        im2_warp = cv2.remap(pyr2[lvl], map_x, map_y,
                             interpolation=cv2.INTER_LINEAR)

        du, dv = lucas_kanade_dense_custom(
            pyr1[lvl], im2_warp, window_size=window_size)
        u += du
        v += dv

    return u, v


def ssd_block_matching_custom(frame1: np.ndarray, frame2: np.ndarray, block_size: int = 16, search_range: int = 4) -> Tuple[np.ndarray, np.ndarray]:
    """Custom SSD block matching implementation."""
    h, w = frame1.shape
    u = np.zeros((h//block_size, w//block_size), dtype=np.float32)
    v = np.zeros((h//block_size, w//block_size), dtype=np.float32)

    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):
            best_score = float('inf')
            best_dx, best_dy = 0, 0
            block = frame1[y:y+block_size, x:x+block_size]

            for dy in range(-search_range, search_range+1):
                for dx in range(-search_range, search_range+1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h - block_size and 0 <= nx < w - block_size:
                        candidate = frame2[ny:ny+block_size, nx:nx+block_size]
                        score = np.sum((block - candidate) ** 2)
                        if score < best_score:
                            best_score = score
                            best_dx, best_dy = dx, dy
            u[y//block_size, x//block_size] = best_dx
            v[y//block_size, x//block_size] = best_dy

    # Upscale to original image size
    u = cv2.resize(u, (w, h), interpolation=cv2.INTER_NEAREST)
    v = cv2.resize(v, (w, h), interpolation=cv2.INTER_NEAREST)
    return u, v

# Library implementations


def horn_schunck_scikit(im1: np.ndarray, im2: np.ndarray, alpha: float = 1.0, max_iter: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """Scikit-image Horn-Schunck implementation (fallback to custom if not available)."""
    if not SKIMAGE_FLOW_AVAILABLE:
        print("Scikit-image optical flow not available, using custom implementation")
        return horn_schunck_custom(im1, im2, alpha=alpha, num_iter=max_iter)

    gray1 = rgb2gray(im1) if im1.ndim == 3 else im1
    gray2 = rgb2gray(im2) if im2.ndim == 3 else im2
    u, v = optical_flow_horn_schunck(
        gray1, gray2, alpha=alpha, num_iter=max_iter)
    return u, v


def lucas_kanade_scikit(im1: np.ndarray, im2: np.ndarray, radius: int = 5, num_levels: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """Scikit-image Lucas-Kanade implementation (fallback to custom if not available)."""
    if not SKIMAGE_FLOW_AVAILABLE:
        print("Scikit-image optical flow not available, using custom implementation")
        return lucas_kanade_dense_custom(im1, im2, window_size=radius*2+1)

    gray1 = rgb2gray(im1) if im1.ndim == 3 else im1
    gray2 = rgb2gray(im2) if im2.ndim == 3 else im2
    u, v = optical_flow_ilk(gray1, gray2, radius=radius, num_levels=num_levels)
    return u, v


def farneback_opencv(im1: np.ndarray, im2: np.ndarray, pyr_scale: float = 0.5, levels: int = 3,
                     winsize: int = 15, iterations: int = 3, poly_n: int = 5, poly_sigma: float = 1.2,
                     flags: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """OpenCV Farneback optical flow implementation."""
    gray1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY) if im1.ndim == 3 else im1
    gray2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY) if im2.ndim == 3 else im2

    flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, pyr_scale, levels, winsize,
                                        iterations, poly_n, poly_sigma, flags)
    u, v = flow[..., 0], flow[..., 1]
    return u, v


def tvl1_opencv(im1: np.ndarray, im2: np.ndarray, tau: float = 0.25, lambda_: float = 0.15,
                theta: float = 0.3, n_scales: int = 5, warps: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """OpenCV TV-L1 optical flow implementation (fallback to Farneback if contrib not available)."""
    gray1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY) if im1.ndim == 3 else im1
    gray2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY) if im2.ndim == 3 else im2

    try:
        tvl1 = cv2.optflow.DualTVL1OpticalFlow_create(
            tau=tau, lambda1=lambda_, theta=theta,
            nscales=n_scales, warps=warps
        )
        flow = tvl1.calc(gray1, gray2, None)
        u, v = flow[..., 0], flow[..., 1]
        return u, v
    except AttributeError:
        print("OpenCV contrib not available, using Farneback instead of TV-L1")
        return farneback_opencv(im1, im2)


# Method collections
CUSTOM_METHODS = {
    "Horn-Schunck (Custom)": horn_schunck_custom,
    "Lucas-Kanade Dense (Custom)": lucas_kanade_dense_custom,
    "Pyramidal Lucas-Kanade (Custom)": pyr_lucas_kanade_custom,
    "SSD Block Matching (Custom)": ssd_block_matching_custom
}

LIBRARY_METHODS = {
    "Horn-Schunck (Scikit)": horn_schunck_scikit,
    "Lucas-Kanade (Scikit)": lucas_kanade_scikit,
    "Farneback (OpenCV)": farneback_opencv,
    "TV-L1 (OpenCV)": tvl1_opencv
}

ALL_METHODS = {**CUSTOM_METHODS, **LIBRARY_METHODS}


def get_method_category(method_name: str) -> str:
    """Get the category of a method (Custom or Library)."""
    if method_name in CUSTOM_METHODS:
        return "Custom"
    elif method_name in LIBRARY_METHODS:
        return "Library"
    else:
        return "Unknown"
