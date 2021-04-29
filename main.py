import cv2
import time
import numpy as np
import VOLUME_CONTROL_USING_HAND_GESTURE.hand_module as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pynput.mouse import Button, Controller

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

## mouse controller
mouse_controller = Controller()
time_skip = 100

while True:

    success, img = cap.read()
    if not success:
        break
    hand_img = detector.findHands(img)
    hand_pos = detector.findPosition(img, draw=False)

    if len(hand_pos) != 0:
        #print(hand_pos)

        x12, y12 = hand_pos[12][1], hand_pos[12][2]
        x16, y16 = hand_pos[16][1], hand_pos[16][2]
        x20, y20 = hand_pos[20][1], hand_pos[20][2]
        x0, y0 = hand_pos[0][1], hand_pos[0][2]
        x1, y1 = hand_pos[4][1], hand_pos[4][2]
        x2, y2 = hand_pos[8][1], hand_pos[8][2]
        x5, y5 = hand_pos[5][1], hand_pos[5][2]
        x4, y4 = hand_pos[4][1], hand_pos[4][2]


        length_all = math.hypot(x12 - x0, y12- y0) + math.hypot(x16 - x0, y16- y0) + math.hypot(x20 - x0, y20- y0)
        #print(length_all)

        if length_all > 500:
            ## volume - movements

            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)


            length = math.hypot(x2 - x1, y2 - y1)

            vol = np.interp(length, [30, 180], [minVol, maxVol])
            volBar = np.interp(length, [30, 180], [400, 150])
            volPer = np.interp(length, [30, 180], [0, 100])
            #print(int(length), vol)
            volume.SetMasterVolumeLevel(vol, None)

            if length < 30:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
        else:
            ## mouse movements
            print(x2, y2)
            mouse_posx = np.interp(x2, [80, 600], [0, 1536])
            mouse_posy = np.interp(y2, [30, 300], [0, 864])
            mouse_controller.position = (mouse_posx, mouse_posy)

            if time_skip != 100:
                if time_skip != 0:
                    time_skip -= 1
                else:
                    time_skip = 100

            length_5_4 = math.hypot(x5 - x4, y5 - y4)
            #print(length_5_4)
            if length_5_4 < 20 and time_skip == 100:
                mouse_controller.press(Button.left)
                mouse_controller.release(Button.left)


            #print(x2, y2)


    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    cv2.imshow("Img", img)
    cv2.waitKey(1)