#!/usr/bin/env python3
"""
Test script to verify that all dependencies and modules are working correctly.
Run this script after installing dependencies to ensure everything is set up properly.
"""

import sys
import importlib
import numpy as np


def test_imports():
    """Test that all required modules can be imported."""
    required_modules = [
        'fastapi',
        'uvicorn',
        'cv2',
        'numpy',
        'scipy',
        'skimage',
        'jinja2',
        'matplotlib',
        'PIL'
    ]

    print("Testing module imports...")
    failed_imports = []

    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing dependencies using: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All modules imported successfully!")
        return True


def test_opencv_methods():
    """Test that OpenCV optical flow methods are available."""
    try:
        import cv2
        print("\nTesting OpenCV methods...")

        # Test basic OpenCV functions
        assert hasattr(
            cv2, 'calcOpticalFlowFarneback'), "Farneback method not available"
        print("✓ Farneback optical flow")

        # Test contrib methods (requires opencv-contrib-python)
        try:
            cv2.optflow.DualTVL1OpticalFlow_create()
            print("✓ TV-L1 optical flow (contrib)")
        except AttributeError:
            print("✗ TV-L1 optical flow (contrib) - install opencv-contrib-python")
            return False

        return True

    except Exception as e:
        print(f"✗ OpenCV test failed: {e}")
        return False


def test_utils_modules():
    """Test that custom utility modules can be imported."""
    try:
        print("\nTesting custom modules...")

        from utils.motion_methods import ALL_METHODS, CUSTOM_METHODS, LIBRARY_METHODS
        print(f"✓ Motion methods: {len(ALL_METHODS)} total methods")

        from utils.evaluation_metrics import compare_methods
        print("✓ Evaluation metrics")

        from utils.visualization import create_flow_visualization
        print("✓ Visualization utilities")

        return True

    except Exception as e:
        print(f"✗ Custom modules test failed: {e}")
        print("Make sure you're running this script from the project root directory")
        return False


def test_basic_functionality():
    """Test basic motion detection functionality with dummy data."""
    try:
        print("\nTesting basic functionality...")

        from utils.motion_methods import horn_schunck_custom

        # Create dummy image data
        img1 = np.random.rand(100, 100).astype(np.float32)
        img2 = img1 + 0.1 * np.random.rand(100, 100).astype(np.float32)

        # Test custom implementation
        u, v = horn_schunck_custom(img1, img2, alpha=1.0, num_iter=5)

        assert u.shape == img1.shape, "Flow field shape mismatch"
        assert v.shape == img1.shape, "Flow field shape mismatch"

        print("✓ Basic motion detection works")
        return True

    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🔧 Motion Detection Tool - Setup Verification")
    print("=" * 50)

    tests = [
        test_imports,
        test_opencv_methods,
        test_utils_modules,
        test_basic_functionality
    ]

    all_passed = True
    for test in tests:
        if not test():
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo start the application, run:")
        print("  uvicorn app:app --reload --host 0.0.0.0 --port 8000")
        print("\nThen open http://localhost:8000 in your browser.")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
