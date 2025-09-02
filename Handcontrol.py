import cv2
import mediapipe as mp
import pyautogui
import numpy as np 
import screen_brightness_control as sbc
from screen_brightness_control import get_brightness
from screen_brightness_control import set_brightness
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Controller as MController

mouse = Controller()
keyboard = MController()


#Function to extract x and y coordinate of the hand landmark 
def cx(x):
    if results.multi_hand_landmarks:
        return results.multi_hand_landmarks[0].landmark[x].x*image_width

def cy(y):
    if results.multi_hand_landmarks:
        return results.multi_hand_landmarks[0].landmark[y].y*image_height

#Setting up User Guide Manual image by importing it into the variable
path = r'C:\Users\yereg\Downloads\Lock.png'
lock = cv2.imread(path)
im = cv2.imread('Lock.png') 

#Putting some mediapipe functions into variables
mp_drawing_styles = mp.solutions.drawing_styles
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

#Setting up video and the resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 860)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

#Some variables
flag, flag1, flagc, flage = True, True, False, False
ind_w, ind_a, ind_s, ind_d = True, True, True, True
movement, jump, shift, cursor, drop, inventory = True, True, True, True, True, True
counter, counter2, counter3 = 0, 0, 1
jump, jump2 = 1, 0
cursorAvgX = [0] * 10
cursorAvgY = [0] * 10
cursorFinalX, cursorFinalY = 0, 0
avgInd = 0
mouse = Controller()
fps = 4
sensitivity = 7

with mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.5,min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue
    #Mirroring our webcam
    image = cv2.cvtColor(cv2.flip(image, 1),1)
    image.flags.writeable = False
    #Setting the video color as in the real world
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    #Getting our webcam resolution
    image_height, image_width, _ = image.shape
    image.flags.writeable = True

    if results.multi_hand_landmarks:

        #finding cursor difference from before frame and current frame
        cx12, cy12 = cx(9), cy(9)
        if flag1:
            cx12_, cy12_ = cx12, cy12
            flag1 = False
        dcx12, dcy12 = cx12 - cx12_, cy12 - cy12_
        cx12_, cy12_ = cx12, cy12

        #storing the difference in array
        if avgInd > 9: avgInd = 0
        cursorAvgX[avgInd] = dcx12
        cursorAvgY[avgInd] = dcy12
        avgInd = avgInd + 1
        cursorFinalX, cursorFinalY = np.mean(np.array(cursorAvgX)), np.mean(np.array(cursorAvgY))

        #finding out if the point of the index finger is going to the right or left
        indexFingerPointX = cx(8)
        indexFingerPivotX = cx(5)
        indexPivotPointDiff = indexFingerPointX-indexFingerPivotX

        #finding out if the point of the index finger is going to the right or left
        thumbFingerPivotX = cx(3)
        thumbFingerPointX = cx(4)
        thumbPivotPointDiff = thumbFingerPointX-thumbFingerPivotX

        #To draw the hand landmarks if needed
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
        
        rightClick = 1

        #Movement Control
        if movement:
            if cy(12) > cy(9) and cy(16) > cy(14):
                cursor, drop, inventory = False, False, False
 
                #Index finger at the right of the pivot
                if (indexPivotPointDiff) > 0:
                    if ind_d:
                        keyboard.release('a')
                        keyboard.release('w')
                        keyboard.release('s')
                        ind_d = False
                    keyboard.press('d')
                    ind_a, ind_s, ind_w = True, True, True

                #Index finger at the left of the pivot
                elif (indexPivotPointDiff) < 0:
                    if ind_a:
                        keyboard.release('w')
                        keyboard.release('s')
                        keyboard.release('d')
                        ind_a = False
                    keyboard.press('a')
                    ind_d, ind_s, ind_w = True, True, True

                #Index finger point bellow first index finger joint
                if (cy(8) > cy(7)) and indexPivotPointDiff < 70 and indexPivotPointDiff > -70:
                    if ind_s:
                        keyboard.release('w')
                        keyboard.release('a')
                        keyboard.release('d')
                        ind_s = False
                    keyboard.press('s')
                    ind_d, ind_a, ind_w = True, True, True

                #Index finger point above first index finger joint
                elif cy(8) < cy(7) and indexPivotPointDiff < 70 and indexPivotPointDiff > -70:
                    if ind_w:
                        keyboard.release('a')
                        keyboard.release('s')
                        keyboard.release('d')
                        ind_w = False
                    keyboard.press('w')
                    cursor = False
                    mouse.release(Button.right)
                    ind_d, ind_s, ind_a = True, True, True
                    
            else:
                cursor, drop, inventory = True, True, True

        #Jumping
        if jump:
            if ((cy(12) < cy(9) or cy(8) < cy(5)) and cy(16) > cy(14) and thumbPivotPointDiff < -20):
                keyboard.press(Key.space)
                drop, inventory = False, False
            else:
                keyboard.release(Key.space)
                drop, inventory = True, True

        #Crouch
        if shift:
            if cy(16) > cy(14) and cy(20) < cy(9):
                keyboard.press(Key.shift)
                drop, inventory = False, False
            else:
                keyboard.release(Key.shift)
                drop, inventory = True, True

        #inventory
        if inventory:
            if cy(12) < cy(9) and cy(16) < cy(14) and cy(20) > cy(17) and cy(8) < cy(5) and thumbPivotPointDiff > 0 and not(flage):
                keyboard.press('e')
                flage = True
                shift, drop, jump, movement = False, False, False, False
            else:
                keyboard.release('e')
                shift, drop, jump, movement = True, True, True, True

        """
                #drop
        if drop:
            if cy(12) < cy(9) and cy(16) < cy(13) and cy(20) < cy(17) and cy(8) < cy(5) and thumbPivotPointDiff > 0:
                keyboard.press('q')
                shift, inventory, jump, movement = False, False, False, False
            else:
                keyboard.release('q')
                shift, inventory, jump, movement = True, True, True, True
        """
        
        #Cursor Control
        if cursor:
            if cy(12) < cy(9) and cy(16) > cy(14) and cy(8) < cy(5):
                flagc = True
                movement, drop, inventory =  False, False, False
            else:
                movement, drop, inventory = True, True, True

            if flagc:
                mouse.move(int(cursorFinalX), int(cursorFinalY))

                #Left 
                if cy(8) > cy(11) and counter == 0:
                    mouse.press(Button.left)
                    counter = 1
                #Right click
                if cy(12) > cy(7) and counter2 == 0:
                    mouse.press(Button.right)
                    counter2 = 1
                #Release left click
                if cy(8) < cy(11) and counter == 1:
                    mouse.release(Button.left)
                    counter = 0
                #Release right click
                if cy(12) < cy(7) and counter2 == 1:
                    mouse.release(Button.right)
                    counter2 = 0
                #Scroll
                if cy(12) > cy(7) and cy(8) > cy(11) and counter3:
                    mouse.scroll(-1, 0)
                    counter3 = False
                flagc = False

        #Resetter
        if cy(12) < cy(9) and cy(16) < cy(14) and cy(20) < cy(17) and cy(8) < cy(5) and thumbPivotPointDiff < -20:
            if flage:
                keyboard.release('e')
                flage = False
            keyboard.release('q')
            keyboard.release('w')
            keyboard.release('a')
            keyboard.release('s')
            keyboard.release('d')
            keyboard.release(Key.space)
            keyboard.release(Key.shift)
            mouse.release(Button.left)
            mouse.release(Button.right)
            counter3 = True

    #Combining User Guide Manual and Webcam
    #Hori = np.concatenate((image,im), axis=1) 

    #Displaying Video
    cv2.imshow(':D', image)

    #Close Program by pressing "p" or the close button
    if cv2.waitKey(1) == ord('p'):
        break
    elif cv2.getWindowProperty(":D",cv2.WND_PROP_VISIBLE) < 1:        
        break 

cap.release()