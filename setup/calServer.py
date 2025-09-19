from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pathlib import Path
from pydantic import BaseModel
import uvicorn, threading, webbrowser
import cv2
import numpy as np
from fastapi.staticfiles import StaticFiles
import json

app = FastAPI()

BASE_DIR   = Path(__file__).parents[1].resolve()
IMAGE_PATH = BASE_DIR/ "images" / "highres (1).jpg"
HTML_PATH  = BASE_DIR / "setup" /"calServer.html"
COORD_FILE = BASE_DIR / "setup" / "coordinates.json"


accepted_reqs = 0


app.mount("/setup", StaticFiles(directory=str(BASE_DIR / "setup")), name="setup")



class Rect(BaseModel):
    x: int
    y: int
    w: int
    h: int



def apply_filter(image_path):
    img = cv2.imread(image_path)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 40, 255])

    mask_combined = cv2.inRange(hsv, lower_white, upper_white)

    mask_bgr = cv2.cvtColor(mask_combined, cv2.COLOR_GRAY2BGR)

    height, width = mask_bgr.shape[:2]

    border_color = (0, 0, 255)

    thickness = 1

    cv2.rectangle(mask_bgr, (0, 0), (width, height), border_color, thickness)


    thirdHeight = height // 3

    thirdOfSect = thirdHeight // 3

    thirdWidth = width // 3

    #RECTANGLES FOR EACH 1/3
    rectangle_color = (0, 0, 0)
    cv2.rectangle(mask_bgr, (0,0), (width, thirdOfSect), rectangle_color, -1)
    cv2.rectangle(mask_bgr, (0, 2 * thirdOfSect), (width, 3*thirdOfSect), rectangle_color, -1)


    cv2.rectangle(mask_bgr, (0,  3 * thirdOfSect), (width, 4 * thirdOfSect), rectangle_color, -1)
    cv2.rectangle(mask_bgr, (0, 5 * thirdOfSect), (width, 6 * thirdOfSect), rectangle_color, -1)

    cv2.rectangle(mask_bgr, (0, (6*thirdOfSect)), (width, (7 * thirdOfSect)), rectangle_color, -1)
    cv2.rectangle(mask_bgr, (0, 8 * thirdOfSect), (width, 9 * thirdOfSect), rectangle_color, -1)

    #HORIZONTAL RECTANGLES FOR EACH 1/3 * W

    cv2.rectangle(mask_bgr, (0, 0), (thirdWidth, 3 * thirdHeight), rectangle_color, -1)
    cv2.rectangle(mask_bgr, (2 * thirdWidth, 0), (3 * thirdWidth, 3 * thirdHeight), rectangle_color, -1)

    #LINE for thirds
    cv2.rectangle(mask_bgr, (0, 0), (width - 1, height - 1), border_color, thickness)
    cv2.line(mask_bgr, (0, thirdHeight), (width, thirdHeight), border_color, 1)
    cv2.line(mask_bgr, (0, thirdHeight * 2), (width, thirdHeight*2), border_color, 1)




    saved_path = BASE_DIR / "setup" / "crops" / "filtered.png"

    cv2.imwrite(str(saved_path), mask_bgr)

    return str(saved_path)


def read_data():
    if COORD_FILE.exists():
        with open(COORD_FILE, 'r') as f:
            return json.load(f)
    else:
        return []
    

def write_data(data):
    try:
        print(type(data))
        print(data)
        with open(COORD_FILE, "w") as f:
            json.dump([data], f, indent=2)
            print("done succesfully")
    except Exception as e:
        print(e)

def add_data(new_data):
    try: 
        exist_data = read_data()
        exist_data.append(new_data)
        with open(COORD_FILE, "w") as f:
            json.dump(exist_data, f, indent=2)
    except Exception as e:
        print(e)

def clear_data():
    try:
        with open(COORD_FILE, "w") as f:
            pass

        print("cleared")
    except Exception as e:
        print(e)
        return []
def undo_last():
    try:
        exist_data = read_data()
        exist_data.pop()
        with open (COORD_FILE, "w") as f:
            json.dump(exist_data, f, indent=2)
        return 1
    except Exception as e:
        return 0
    


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"))

@app.get("/image")
def get_image():
    print("getting here")
    if not IMAGE_PATH.exists():
        return HTMLResponse(f"Image not found: {IMAGE_PATH}", status_code=404)
    return FileResponse(str(IMAGE_PATH))

@app.post("/rect")
def rect(p: Rect):
    data = [p.x, p.y, p.w, p.h]
    print(data)
    x, y, w, h = data
    print(f"[RECT] x={x}, y={y}, w={w}, h={h}")
    read_image = cv2.imread(IMAGE_PATH)
    try:
        cropped = read_image[y: y+h, x: x+w]
        path = BASE_DIR / "setup" / "crops" / "saved.png"
        cv2.imwrite(path, cropped)
        apply_filter(path)
        
        return JSONResponse({"ok": True, "control_path": "setup/crops/saved.png", "filtered_path": "setup/crops/filtered.png"})

        
    except Exception as e:
        print(e)
        return JSONResponse({"error": e, "status": 404})
    

@app.post("/accepted")
def accepted(p: Rect):
    global accepted_reqs
    xScale = (1920/1280)
    yScale = (1080/720)
    try:
        finalX = round(p.x * xScale)
        finalY = round(p.y * yScale)
        finalW = round(p.w * xScale)
        finalH = round(p.h * yScale)
        data = [finalX, finalY, finalW, finalH]
        if accepted_reqs == 0:
            write_data(data)
        else:
            add_data(data)
        accepted_reqs+=1
        print(accepted_reqs)
        return JSONResponse({"message": "accepted", "status": 200})
    except Exception as e:
        return JSONResponse({"error": e, "status": 404})

@app.post("/cleared_xyz_parrow")
def cleared():
    try:
        clear_data()
        accepted_reqs = 0
        return JSONResponse({"list": "cleared", "status":200})
    except Exception as e:
        print(e)
        return JSONResponse({"list": "not cleared", "status": 404})

@app.post("/undo_last")
def undo():
    try:
        return_undo = undo_last()
        if return_undo:
            print("did undo")
            accepted_reqs -= 1
            return JSONResponse({"undo": "done", "status": 200})
    except:
        return JSONResponse({"status": 404})



if __name__ == "__main__":
    threading.Timer(0.5, lambda: webbrowser.open("http://127.0.0.1:8000/")).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
