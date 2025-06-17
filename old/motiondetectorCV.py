import cv2
import numpy as np

def flow_farneback(img1: np.ndarray, img2: np.ndarray, pyr_scale: float = 0.5, levels: int = 3, winsize: int = 15, iterations: int = 3, poly_n: int = 5, poly_sigma: float = 1.2, flags: int = 0) -> np.ndarray:
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) if img1.ndim == 3 else img1
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) if img2.ndim == 3 else img2
    
    flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, pyr_scale, levels, winsize, iterations, poly_n, poly_sigma, flags)
    u, v = flow[..., 0], flow[..., 1]
    return u, v


def flow_pyr_lk(img1: np.ndarray, img2: np.ndarray, prev_pts: np.ndarray, win_size: tuple = (21, 21), max_level: int = 3, criteria: tuple = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)) -> tuple:
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) if img1.ndim == 3 else img1
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) if img2.ndim == 3 else img2

    new_pts, status, err = cv2.calcOpticalFlowPyrLK(
        gray1, gray2, prev_pts, None,
        winSize=win_size,
        maxLevel=max_level,
        criteria=criteria
    )
    return new_pts, status, err


def flow_dual_tvl1(img1: np.ndarray, img2: np.ndarray, tau: float = 0.25, lambda_: float = 0.15, theta: float = 0.3, n_scales: int = 5, warps: int = 5) -> np.ndarray:
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) if img1.ndim == 3 else img1
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) if img2.ndim == 3 else img2

    tvl1 = cv2.optflow.DualTVL1OpticalFlow_create(
        tau=tau, lambda1=lambda_, theta=theta,
        nscales=n_scales, warps=warps
    )
    flow = tvl1.calc(gray1, gray2, None)
    u, v = flow[..., 0], flow[..., 1]
    return u, v