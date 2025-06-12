from fastapi import FastAPI, Response, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from motiondetector import *

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

@app.post("/submit")
async def submit_data(image1: UploadFile = File(...), image2: UploadFile = File(...), method_received: str = Form(...)):
    method_map = {
        "horn_schunck": motion_detect_horn_schunck,
        "pyr_lucas_kanade": motion_detect_pyr_lucas_kanade,
        "ssd": motion_detect_ssd
    }
    data1 = await image1.read()
    data2 = await image2.read()

    arr1 = np.frombuffer(data1, np.uint8)
    arr2 = np.frombuffer(data2, np.uint8)
    frame1 = cv2.imdecode(arr1, cv2.IMREAD_COLOR)
    frame2 = cv2.imdecode(arr2, cv2.IMREAD_COLOR)

    if method_received not in method_map:
        return Response(status_code=400, content=b"Unknown method")
    result_img = method_map[method_received](cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY), cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY))

    success, buffer = cv2.imencode('.png', result_img)
    if not success:
        return Response(status_code=500, content=b"Encoding failed")

    return Response(content=buffer.tobytes(), media_type="image/png")