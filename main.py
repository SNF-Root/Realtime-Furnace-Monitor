import cv2
import numpy as np
import os
import time
import cv2.aruco as aruco

#lets try a dynamic cropping and fall into static cropping if it does not work too well

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



    fixed_points = [[static_points[0][0] + 32, static_points[0][1] + 45, 25, 55],
                    [static_points[0][0] + 32, static_points[0][1] + 158, 25, 55],
                    [static_points[0][0] + 32, static_points[0][1] + 286, 25, 55],
                    [static_points[0][0] + 38, static_points[0][1] + 404, 25, 55],
                    [static_points[1][0] + 56, static_points[1][1] + 54, 25, 55],
                    [static_points[1][0] + 56, static_points[1][1] + 187, 25, 55],
                    [static_points[1][0] + 59, static_points[1][1] + 317, 25, 55],
                    [static_points[1][0] + 59, static_points[1][1] + 450, 25, 55],
                    [static_points[2][0] - 12, static_points[2][1] + 42, 25, 55],
                    [static_points[2][0] - 9, static_points[2][1] + 175, 25, 55],
                    [static_points[2][0] - 9, static_points[2][1] + 303, 25, 55],
                    [static_points[2][0] - 10, static_points[2][1] + 428, 25, 55]]

    x, y, w, h = fixed_points[tube]

    cropped = readImage[y: y+h, x: x+w]
    cv2.imwrite(f"preprocess/croppedimg{tube}.jpg",  cropped)
    return cropped

#processes the image into black and white
def detectLight(image, tube):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 40, 255])

    mask_combined = cv2.inRange(hsv, lower_white, upper_white)

    kernel = np.ones((2, 2), np.uint8)
    mask_eroded = cv2.erode(mask_combined, kernel, iterations=1)

    mask_bgr = cv2.cvtColor(mask_eroded, cv2.COLOR_GRAY2BGR)

    height, width = mask_bgr.shape[:2]


    border_color = (0, 0, 255)  # Red in BGR
    thickness = 2
    cv2.rectangle(mask_bgr, (0, 0), (width - 1, height - 1), border_color, thickness)


    third = height // 3
    cv2.line(mask_bgr, (0, third), (width, third), border_color, 1)
    cv2.line(mask_bgr, (0, third * 2), (width, third * 2), border_color, 1)




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

 
    if(top_sum > 100):
        # print(f"tube {tube+1}: RED ON")
        red = True
    if(middle_sum > 100):
        # print(f"tube {tube+1}: ORANGE ON")
        orange =  True
    if(bottom_sum > 100):
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

    img = cv2.imread("images/highres.jpg")
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", show_coordinates)

    while True:
        cv2.imshow("image", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()

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
# detectLight(img)
# processedPath = "preprocess/processedImage.png"
# classifyColor(processedPath)
# textinput = input("q to quit(): ")
# if(textinput == 'q'):
#     os.remove("preprocess/processedImage.png")

# capture1080p()
# configure_points()



while True:

    capture1080p()
    capture1080p()

    static_points = arucocap()
    if len(static_points) != 3:
        break

    for i in range(0, 12):
        croppedImg = cropStaticFurnaces(static_points, "images/highres.jpg", i)
        filePath = detectLight(croppedImg, i)
        # filePath = f"preprocess/processedImage{i}.png"
        valid = classifyColor(filePath, i)
        if not valid:
            break
    
    if i < 12:
        continue
    else:
        time.sleep(120)



# capture1080p()
# capture1080p()
# for i in range(12):
#     cropStaticFurnaces("images/highres.jpg", i)

# for i in range(5):
#     capture1080p(i)




