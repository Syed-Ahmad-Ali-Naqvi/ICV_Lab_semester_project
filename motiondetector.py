import numpy as np
import cv2
from scipy.signal import convolve2d

def detect_motion_direction(image1, image2, method='horn_schunck'):
    """
    Detects the direction of motion between two images.
    
    Parameters:
    - image1: First input image (numpy array).
    - image2: Second input image (numpy array).
    
    Returns:
    - 
    """
    img1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    
    if method == 'horn_schunck':
        return motion_detect_horn_schunck(img1, img2)
    elif method == 'pyr_lucas_kanade':
        return motion_detect_pyr_lucas_kanade(img1, img2)
    elif method == 'SSD':
        return motion_detect_ssd(img1, img2)
    else:
        raise ValueError("Unknown method: {}".format(method))

def horn_schunck(im1, im2, alpha=1.0, num_iter=100):
    im1 = im1.astype(np.float32)
    im2 = im2.astype(np.float32)

    kernel_x = np.array([[-1, 1], [-1, 1]]) * 0.25
    kernel_y = np.array([[-1, -1], [1, 1]]) * 0.25
    kernel_t = np.ones((2, 2)) * 0.25

    Ix = convolve2d(im1, kernel_x, boundary='symm', mode='same') + convolve2d(im2, kernel_x, boundary='symm', mode='same')
    Iy = convolve2d(im1, kernel_y, boundary='symm', mode='same') + convolve2d(im2, kernel_y, boundary='symm', mode='same')
    It = convolve2d(im2, kernel_t, boundary='symm', mode='same') - convolve2d(im1, kernel_t, boundary='symm', mode='same')

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

def lucas_kanade_dense(im1, im2, window_size=5):
    im1 = im1.astype(np.float32)
    im2 = im2.astype(np.float32)

    Ix = cv2.Sobel(im1, cv2.CV_32F, 1, 0, ksize=3) + cv2.Sobel(im2, cv2.CV_32F, 1, 0, ksize=3)
    Iy = cv2.Sobel(im1, cv2.CV_32F, 0, 1, ksize=3) + cv2.Sobel(im2, cv2.CV_32F, 0, 1, ksize=3)
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

def pyr_lucas_kanade(im1, im2, num_levels=3, window_size=5):
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
        im2_warp = cv2.remap(pyr2[lvl], map_x, map_y, interpolation=cv2.INTER_LINEAR)

        du, dv = lucas_kanade_dense(pyr1[lvl], im2_warp, window_size=window_size)
        u += du
        v += dv

    return u, v

def ssd_block_matching(frame1, frame2, block_size=16, search_range=4):
    h, w = frame1.shape
    motion_vectors = np.zeros((h//block_size, w//block_size, 2), dtype=np.int32)

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
            motion_vectors[y//block_size, x//block_size] = [best_dx, best_dy]
    return motion_vectors

def draw_motion_vectors(frame, motion_vectors, block_size=16):
    output = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    for y in range(0, motion_vectors.shape[0]):
        for x in range(0, motion_vectors.shape[1]):
            dx, dy = motion_vectors[y, x]
            start = (x*block_size, y*block_size)
            end = (start[0] + dx*2, start[1] + dy*2)
            cv2.arrowedLine(output, start, end, (0, 255, 0), 1, tipLength=0.4)
    return output

def motion_detect_ssd(frame1, frame2):
    motion_vectors = ssd_block_matching(frame1, frame2)
    return draw_motion_vectors(frame1, motion_vectors)

def motion_detect_horn_schunck(frame1, frame2):
    u, v = horn_schunck(frame1, frame2)
    h, w = frame1.shape
    flow_image = np.zeros((h, w, 3), dtype=np.uint8)
    flow_image[..., 0] = frame1
    flow_image[..., 1] = frame1
    flow_image[..., 2] = frame1
    for i in range(0, h, 10):
        for j in range(0, w, 10):
            cv2.arrowedLine(flow_image, (j, i), (int(j + u[i, j]), int(i + v[i, j])), (0, 255, 0), 1, tipLength=0.2)
    return flow_image

def motion_detect_pyr_lucas_kanade(frame1, frame2):
    u, v = pyr_lucas_kanade(frame1, frame2)
    h, w = frame1.shape
    flow_image = np.zeros((h, w, 3), dtype=np.uint8)
    flow_image[..., 0] = frame1
    flow_image[..., 1] = frame1
    flow_image[..., 2] = frame1
    for i in range(0, h, 10):
        for j in range(0, w, 10):
            cv2.arrowedLine(flow_image, (j, i), (int(j + u[i, j]), int(i + v[i, j])), (0, 255, 0), 1, tipLength=0.2)
    return flow_image