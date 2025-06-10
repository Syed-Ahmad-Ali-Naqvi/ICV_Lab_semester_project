from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Request, File, UploadFile
from fastapi.responses import JSONResponse
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

# Get both images
@app.post("/submit")
async def submit_data(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    # read bytes
    data1 = await image1.read()
    data2 = await image2.read()

    print(f"Received files: {image1.filename}, {image2.filename}")

    return JSONResponse({
        "filename1": image1.filename,
        "filename2": image2.filename,
        "message": "Received both files!"
        # …plus any results you want to send back…
    })