from fastapi import FastAPI, Response, Form, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import numpy as np
import cv2
import json
from utils.motion_methods import ALL_METHODS, CUSTOM_METHODS, LIBRARY_METHODS, get_method_category
from utils.evaluation_metrics import compare_methods
from utils.visualization import create_flow_visualization, create_comparison_grid

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/single-method")
async def single_method_analysis(image1: UploadFile = File(...), image2: UploadFile = File(...), method_name: str = Form(...)):
    """Process single method and return visualization with metrics."""
    try:
        data1 = await image1.read()
        data2 = await image2.read()

        arr1 = np.frombuffer(data1, np.uint8)
        arr2 = np.frombuffer(data2, np.uint8)
        frame1 = cv2.imdecode(arr1, cv2.IMREAD_COLOR)
        frame2 = cv2.imdecode(arr2, cv2.IMREAD_COLOR)

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        if method_name not in ALL_METHODS:
            return JSONResponse(status_code=400, content={"error": "Unknown method"})

        method_func = ALL_METHODS[method_name]
        results = compare_methods(gray1, gray2, {method_name: method_func})

        if not results[method_name]["success"]:
            return JSONResponse(status_code=500, content={"error": results[method_name].get("error", "Method failed")})

        # Use the flow vectors from compare_methods to avoid double execution
        u, v = results[method_name]["flow_vectors"]

        result_img = create_flow_visualization(u, v, gray1, scale=3, step=15)

        success, buffer = cv2.imencode('.png', result_img)
        if not success:
            return JSONResponse(status_code=500, content={"error": "Encoding failed"})

        return Response(content=buffer.tobytes(), media_type="image/png")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/single-method-metrics")
async def single_method_metrics(image1: UploadFile = File(...), image2: UploadFile = File(...), method_name: str = Form(...)):
    """Get metrics for a single method without running all methods."""
    try:
        data1 = await image1.read()
        data2 = await image2.read()

        arr1 = np.frombuffer(data1, np.uint8)
        arr2 = np.frombuffer(data2, np.uint8)
        frame1 = cv2.imdecode(arr1, cv2.IMREAD_COLOR)
        frame2 = cv2.imdecode(arr2, cv2.IMREAD_COLOR)

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        if method_name not in ALL_METHODS:
            return JSONResponse(status_code=400, content={"error": "Unknown method"})

        method_func = ALL_METHODS[method_name]
        results = compare_methods(gray1, gray2, {method_name: method_func})

        # Add method category and remove flow_vectors for JSON response
        result = results[method_name].copy()
        result["category"] = get_method_category(method_name)
        if "flow_vectors" in result:
            # Remove heavy arrays from JSON response
            del result["flow_vectors"]

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/compare-methods")
async def compare_all_methods(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    """Compare all methods and return comprehensive analysis."""
    try:
        data1 = await image1.read()
        data2 = await image2.read()

        arr1 = np.frombuffer(data1, np.uint8)
        arr2 = np.frombuffer(data2, np.uint8)
        frame1 = cv2.imdecode(arr1, cv2.IMREAD_COLOR)
        frame2 = cv2.imdecode(arr2, cv2.IMREAD_COLOR)

        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Compare all methods
        results = compare_methods(gray1, gray2, ALL_METHODS)

        # Add method categories and remove flow_vectors for JSON response
        for method_name in results:
            results[method_name]["category"] = get_method_category(method_name)
            if "flow_vectors" in results[method_name]:
                # Remove heavy arrays from JSON response
                del results[method_name]["flow_vectors"]

        return JSONResponse(content=results)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/visualize-comparison")
async def visualize_comparison(image1: UploadFile = File(...), image2: UploadFile = File(...), selected_methods: str = Form(...)):
    """Create grid visualization comparing selected methods."""
    try:
        method_names = json.loads(selected_methods)

        data1 = await image1.read()
        data2 = await image2.read()

        arr1 = np.frombuffer(data1, np.uint8)
        arr2 = np.frombuffer(data2, np.uint8)
        frame1 = cv2.imdecode(arr1, cv2.IMREAD_COLOR)
        frame2 = cv2.imdecode(arr2, cv2.IMREAD_COLOR)

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        selected_method_funcs = {
            name: ALL_METHODS[name] for name in method_names if name in ALL_METHODS}
        flow_results = {}

        for method_name, method_func in selected_method_funcs.items():
            try:
                u, v = method_func(gray1, gray2)
                flow_results[method_name] = (u, v)
            except Exception as e:
                print(f"Method {method_name} failed: {e}")
                continue

        if flow_results:
            grid_image = create_comparison_grid(flow_results, gray1)
        else:
            grid_image = gray1

        success, buffer = cv2.imencode('.png', grid_image)
        if not success:
            return JSONResponse(status_code=500, content={"error": "Encoding failed"})

        return Response(content=buffer.tobytes(), media_type="image/png")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/available-methods")
async def get_available_methods():
    """Get list of available methods categorized."""
    return JSONResponse(content={
        "custom_methods": list(CUSTOM_METHODS.keys()),
        "library_methods": list(LIBRARY_METHODS.keys()),
        "all_methods": list(ALL_METHODS.keys())
    })
