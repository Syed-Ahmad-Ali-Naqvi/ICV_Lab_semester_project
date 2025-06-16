import numpy as np
import time
from typing import Tuple, Dict, Any


def calculate_angular_error(u_true: np.ndarray, v_true: np.ndarray,
                            u_pred: np.ndarray, v_pred: np.ndarray) -> float:
    """Calculate angular error between true and predicted flow fields."""
    # Normalize flow vectors
    mag_true = np.sqrt(u_true**2 + v_true**2)
    mag_pred = np.sqrt(u_pred**2 + v_pred**2)

    # Avoid division by zero
    valid_mask = (mag_true > 1e-6) & (mag_pred > 1e-6)

    if not np.any(valid_mask):
        return 0.0

    # Calculate cosine of angle between vectors
    dot_product = (u_true * u_pred + v_true * v_pred)[valid_mask]
    cos_angle = dot_product / (mag_true[valid_mask] * mag_pred[valid_mask])

    # Clip to avoid numerical errors
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    # Calculate angular error in degrees
    angular_error = np.rad2deg(np.arccos(np.abs(cos_angle)))
    return np.mean(angular_error)


def calculate_endpoint_error(u_true: np.ndarray, v_true: np.ndarray,
                             u_pred: np.ndarray, v_pred: np.ndarray) -> float:
    """Calculate endpoint error between true and predicted flow fields."""
    error = np.sqrt((u_true - u_pred)**2 + (v_true - v_pred)**2)
    return np.mean(error)


def calculate_mse(u_true: np.ndarray, v_true: np.ndarray,
                  u_pred: np.ndarray, v_pred: np.ndarray) -> float:
    """Calculate Mean Squared Error."""
    mse_u = np.mean((u_true - u_pred)**2)
    mse_v = np.mean((v_true - v_pred)**2)
    return (mse_u + mse_v) / 2


def calculate_mae(u_true: np.ndarray, v_true: np.ndarray,
                  u_pred: np.ndarray, v_pred: np.ndarray) -> float:
    """Calculate Mean Absolute Error."""
    mae_u = np.mean(np.abs(u_true - u_pred))
    mae_v = np.mean(np.abs(v_true - v_pred))
    return (mae_u + mae_v) / 2


def measure_execution_time(func, *args, **kwargs) -> Tuple[Any, float]:
    """Measure execution time of a function."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time


def calculate_flow_statistics(u: np.ndarray, v: np.ndarray) -> Dict[str, float]:
    """Calculate basic statistics of flow field."""
    magnitude = np.sqrt(u**2 + v**2)
    return {
        "mean_magnitude": float(np.mean(magnitude)),
        "max_magnitude": float(np.max(magnitude)),
        "std_magnitude": float(np.std(magnitude)),
        "mean_u": float(np.mean(u)),
        "mean_v": float(np.mean(v)),
        "std_u": float(np.std(u)),
        "std_v": float(np.std(v))
    }


def compare_methods(frame1: np.ndarray, frame2: np.ndarray, methods: Dict[str, callable]) -> Dict[str, Dict[str, Any]]:
    """Compare multiple optical flow methods and return results with metrics."""
    results = {}
    flows = {}

    # Calculate flows for all methods
    for method_name, method_func in methods.items():
        try:
            (u, v), execution_time = measure_execution_time(
                method_func, frame1, frame2)
            flows[method_name] = (u, v)

            # Calculate basic statistics
            stats = calculate_flow_statistics(u, v)

            results[method_name] = {
                "execution_time": round(execution_time, 4),
                "statistics": stats,
                "flow_vectors": (u, v),  # Include flow vectors in results
                "success": True
            }
        except Exception as e:
            results[method_name] = {
                "execution_time": 0,
                "statistics": {},
                "flow_vectors": None,
                "success": False,
                "error": str(e)
            }

    # Calculate cross-method comparisons (using first successful method as reference)
    reference_method = None
    for method_name, result in results.items():
        if result["success"]:
            reference_method = method_name
            break

    if reference_method and len([r for r in results.values() if r["success"]]) > 1:
        ref_u, ref_v = flows[reference_method]

        for method_name, result in results.items():
            if result["success"] and method_name != reference_method:
                u, v = flows[method_name]

                # Ensure same dimensions for comparison
                min_h = min(ref_u.shape[0], u.shape[0])
                min_w = min(ref_u.shape[1], u.shape[1])

                ref_u_crop = ref_u[:min_h, :min_w]
                ref_v_crop = ref_v[:min_h, :min_w]
                u_crop = u[:min_h, :min_w]
                v_crop = v[:min_h, :min_w]

                result["comparison_metrics"] = {
                    "mse": round(calculate_mse(ref_u_crop, ref_v_crop, u_crop, v_crop), 4),
                    "mae": round(calculate_mae(ref_u_crop, ref_v_crop, u_crop, v_crop), 4),
                    "endpoint_error": round(calculate_endpoint_error(ref_u_crop, ref_v_crop, u_crop, v_crop), 4),
                    "angular_error": round(calculate_angular_error(ref_u_crop, ref_v_crop, u_crop, v_crop), 4)
                }

    return results
