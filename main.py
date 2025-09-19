import cv2
import numpy as np
import os
import time
import cv2.aruco as aruco
from pathlib import Path
import json

#lets try a dynamic cropping and fall into static cropping if it does not work too well


BASE_DIR   = Path(__file__).parents[0].resolve()

COORD_FILE  = BASE_DIR / "setup" /"coordinates.json"

def arucocap():
    frame = cv2.imread("images/highres.jpg")
    allowed_markers = {0, 1, 2}

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(frame)

    position_list = []

    if markerIds is not None:
        markerIds = markerIds.flatten()
        print(f"Detected IDs: {markerIds}")

        filteredCorners = []
        filteredIds = []

        for i, id in enumerate(markerIds):
            if id in allowed_markers:
                print(f"markerId: {id}")
                filteredCorners.append(markerCorners[i])
                filteredIds.append([id])


                corner = markerCorners[i].reshape(-1, 2)[3]
                position_list.append([int(corner[0]), int(corner[1])])
            else:
                print(f"Ignoring marker: {id}")

        if filteredCorners:
            cv2.aruco.drawDetectedMarkers(frame, filteredCorners, np.array(filteredIds))
        
        position_list.sort()



    return position_list

def cropStaticFurnaces(static_points, imagePath, tube):
    readImage = cv2.imread(imagePath)

    x, y, w, h = static_points[tube]

    cropped = readImage[y: y+h, x: x+w]
    cv2.imwrite(f"preprocess/croppedimg{tube}.jpg",  cropped)
    return cropped



#processes the image into black and white
def apply_filter(image, tube):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 40, 255])

    mask_combined = cv2.inRange(hsv, lower_white, upper_white)

    mask_bgr = cv2.cvtColor(mask_combined, cv2.COLOR_GRAY2BGR)

    height, width = mask_bgr.shape[:2]


    border_color = (0, 0, 255)  # Red in BGR
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

    save_path = f"preprocess/processedImage{tube}.png"
    cv2.imwrite(save_path, mask_bgr)

    return save_path







#tells us what color is on, based on position of the light
def classifyColor(image, tube):
    img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

    if img is None:
        print("file not found")

    height, width = img.shape
    
    section = height // 3

    top = img[0: section, :]
    middle = img[section : section * 2, :]
    bottom = img[section * 2: , :]


    top_array = []
    top_sum = 0
    for y in range(top.shape[0]):
        for x in range(top.shape[1]):
            if(top[y, x] ==  255):
                top_array.append(1)
                top_sum+=1
            else:
                top_array.append(0)
    
    middle_sum = 0
    middle_array = []
    for y in range(middle.shape[0]):
        for x in range(middle.shape[1]):
            if(middle[y, x] == 255):
                middle_array.append(1)
                middle_sum+=1
            else:
                middle_array.append(0)
    

        
    bottom_sum = 0
    bottom_array = []
    for y in range(bottom.shape[0]):
        for x in range(bottom.shape[1]):
            if(bottom[y, x] == 255):
                bottom_array.append(1)
                bottom_sum+=1
            else:
                bottom_array.append(0)
   


    # print("top sum: ", top_sum)
    # print("middle_sum: ",  middle_sum)
    # print("bottom_sum: ",  bottom_sum)

    red = False
    orange = False
    green = False

 
    if(top_sum > 0):
        # print(f"tube {tube+1}: RED ON")
        red = True
    if(middle_sum > 0):
        # print(f"tube {tube+1}: ORANGE ON")
        orange =  True
    if(bottom_sum > 0):
        # print(f"tube {tube+1}: GREEN ON")
        green = True

    print(f"TUBE {tube + 1}: ", top_sum, middle_sum, bottom_sum)

    if(not red and not orange and not green):
        print(f"tube {tube + 1}: VIEW OBSTRUCTED!")
        return False   
    else:
        if orange and green:
            print(f"Tube {tube+1}: Waiting for USER Input")
        elif green and red:
            print(f"Tube {tube+1}: WAITING FOR WAFER LOAD")
        else:
            if red:
                print(f"Tube {tube+1}: ERROR! CONTACT STAFF")
            elif green:
                print(f"Tube {tube+1}: Running Recipe")
            elif orange:
                print(f"Tube {tube+1}: IDLE & Ready")


    print('--------------------------------------------')

def mitigate_bleeding(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    kernel = np.ones((3, 3), np.uint8)

    cleaned = cv2.erode(thresh, kernel, iterations = 1)
    print("got here")
    return cleaned 

def configure_points():
    def show_coordinates(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"X: {x}, Y: {y}")
    img = cv2.imread("images/highres (1).jpg")
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", show_coordinates)


    while True:
        cv2.imshow("image", img)
        key = cv2.waitKey(1) & 0xFF
        if (key == ord("j") or key == ord("J")):
            try:
                window_existence = cv2.getWindowProperty("crop", cv2.WND_PROP_VISIBLE)
                if (window_existence):
                    saved_coordinates.append(pressed_coordinates[-1])
                    print(f"""saved coordinates: {saved_coordinates}""")
                    cv2.destroyWindow("crop")
                    cv2.destroyWindow("no mask crop")
            except:
                pass
        elif (key == ord("k") or key == ord("K")):
            try: 
                if (cv2.getWindowProperty("crop", cv2.WND_PROP_VISIBLE)):
                    cv2.destroyWindow("crop")
                    cv2.destroyWindow("no mask crop")
            except:
                pass
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
    return saved_coordinates

def capture1080p():
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


    ret, frame = cap.read()

    if not ret:
        print("cant see")
    else:
        height, width = frame.shape[:2]
        print(height, width)


    cv2.imwrite("images/highres.jpg", frame)

    cap.release()



# img = cv2.imread("images/stack.jpeg")
# apply_filter(img)
# processedPath = "preprocess/processedImage.png"
# classifyColor(processedPath)
# textinput = input("q to quit(): ")
# if(textinput == 'q'):
#     os.remove("preprocess/processedImage.png")

# capture1080p()



def read_data():
    if COORD_FILE.exists():
        with open(COORD_FILE, 'r') as f:
            return json.load(f)
    else:
        print("array has nothing")
        return []


# while True:

#     # capture1080p()
#     # capture1080p()

#     # static_points = arucocap()


#     static_points = read_data()

#     print(static_points)
#     print(len(static_points))
    

#     time.sleep(120)

#     cropStaticFurnaces(static_points, "images/highres (1).jpg", 0)

#     # if len(static_points) != 3:
#     #     break

#     for i in range(0, 12):
#         croppedImg = cropStaticFurnaces(static_points, "images/highres (1).jpg", i)
#         filePath = apply_filter(croppedImg, i)
#         # filePath = f"preprocess/processedImage{i}.png"
#         valid = classifyColor(filePath, i)
#         if not valid:
#             break
    
#     if i < 12: #means that we didnt get to all of the furnace lights because of some distraction
#         continue
#     else:
#         time.sleep(120)




static_points = read_data()


print(static_points)
print(len(static_points))




cropped = cropStaticFurnaces(static_points, "images/highres (1).jpg", 0)
filter_cropped = apply_filter(cropped, 0)
classifyColor(filter_cropped, 0)

# capture1080p()
# capture1080p()
# for i in range(12):
#     cropStaticFurnaces("images/highres.jpg", i)

# for i in range(5):
#     capture1080p(i)




