import numpy as np
import cv2
from typing import Tuple


def create_flow_visualization(u: np.ndarray, v: np.ndarray, background_image: np.ndarray = None,
                              scale: float = 1.0, step: int = 10) -> np.ndarray:
    """
    Create a visualization of optical flow field with arrows.

    Args:
        u, v: Flow field components
        background_image: Background image to overlay arrows on
        scale: Scale factor for arrow visualization
        step: Step size for arrow grid

    Returns:
        RGB image with flow visualization
    """
    h, w = u.shape

    # Create background
    if background_image is not None:
        if len(background_image.shape) == 3:
            flow_image = background_image.copy()
        else:
            flow_image = cv2.cvtColor(background_image, cv2.COLOR_GRAY2BGR)
    else:
        flow_image = np.zeros((h, w, 3), dtype=np.uint8)

    # Draw arrows
    for y in range(step//2, h, step):
        for x in range(step//2, w, step):
            if y < h and x < w:
                start_point = (x, y)
                end_point = (int(x + u[y, x] * scale),
                             int(y + v[y, x] * scale))

                # Ensure end point is within image bounds
                end_point = (
                    max(0, min(w-1, end_point[0])),
                    max(0, min(h-1, end_point[1]))
                )

                # Calculate arrow color based on magnitude
                magnitude = np.sqrt(u[y, x]**2 + v[y, x]**2)
                if magnitude > 0.5:  # Only draw significant vectors
                    color = (0, 255, 0)  # Green arrows
                    cv2.arrowedLine(flow_image, start_point,
                                    end_point, color, 1, tipLength=0.3)

    return flow_image


def create_color_coded_flow(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    Create color-coded flow visualization (HSV encoding).

    Args:
        u, v: Flow field components

    Returns:
        RGB image with color-coded flow
    """
    h, w = u.shape

    # Calculate magnitude and angle
    magnitude = np.sqrt(u**2 + v**2)
    angle = np.arctan2(v, u)

    # Create HSV image
    hsv = np.zeros((h, w, 3), dtype=np.uint8)

    # Hue represents direction (0-180 for OpenCV)
    hsv[..., 0] = ((angle + np.pi) / (2 * np.pi) * 180).astype(np.uint8)

    # Saturation is always max
    hsv[..., 1] = 255

    # Value represents magnitude
    magnitude_normalized = np.clip(
        magnitude / (np.max(magnitude) + 1e-6) * 255, 0, 255)
    hsv[..., 2] = magnitude_normalized.astype(np.uint8)

    # Convert to RGB
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    return rgb


def create_magnitude_heatmap(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    Create magnitude heatmap visualization.

    Args:
        u, v: Flow field components

    Returns:
        RGB heatmap image
    """
    magnitude = np.sqrt(u**2 + v**2)

    # Normalize magnitude to 0-255
    magnitude_normalized = np.clip(
        magnitude / (np.max(magnitude) + 1e-6) * 255, 0, 255).astype(np.uint8)

    # Apply colormap
    heatmap = cv2.applyColorMap(magnitude_normalized, cv2.COLORMAP_JET)

    return cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)


def create_comparison_grid(flow_results: dict, original_image: np.ndarray) -> np.ndarray:
    """
    Create a grid comparison of different flow methods.

    Args:
        flow_results: Dictionary of method_name -> (u, v) pairs
        original_image: Original image for reference

    Returns:
        Grid image showing all methods
    """
    methods = list(flow_results.keys())
    n_methods = len(methods)

    if n_methods == 0:
        return original_image

    # Calculate grid dimensions
    cols = min(3, n_methods)
    rows = (n_methods + cols - 1) // cols

    h, w = original_image.shape[:2]

    # Create grid image
    grid_h = rows * h
    grid_w = cols * w
    grid_image = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)

    for idx, method_name in enumerate(methods):
        row = idx // cols
        col = idx % cols

        u, v = flow_results[method_name]

        # Create visualization for this method
        flow_vis = create_flow_visualization(
            u, v, original_image, scale=3, step=15)

        # Place in grid
        y_start = row * h
        y_end = y_start + h
        x_start = col * w
        x_end = x_start + w

        grid_image[y_start:y_end, x_start:x_end] = flow_vis

        # Add method name
        cv2.putText(grid_image, method_name, (x_start + 10, y_start + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return grid_image
