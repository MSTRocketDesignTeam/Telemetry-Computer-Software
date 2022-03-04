import time
import cv2
import random as r
from datetime import datetime, date
import keyboard
import math

winName = "RDT Tracking"
sat = cv2.imread("imgs/sat3.PNG")
#sat = cv2.resize(sat, None, fx=.5605, fy=.5584, interpolation=cv2.INTER_AREA) #Resizing if needed
# (LATITUDE, LONGITUDE)
# 6.4 by 6.4 mile perimeter with launch pad in middle
# Pixels are 810x810

topl = (37.2138385, -97.797595)
botl = (37.1223676, -97.7968443)
topr = (37.2117854, -97.6806518)
botr = (37.122033, -97.6816494)
lp = (37.1676624, -97.7399083)
toplat = 37.212
botlat = 37.122
leftlon = -97.797
rightlon = -97.681
padx = 405
pady = 405
xmax = 810
ymax = 810

maindir = r.randint(1, 4) #Randomly decides on main compass direction
start = (padx, pady) #Launch pad pixel cords
rpathx = start[0]
rpathy = start[1]

def cordgen():
    secdir = r.randint(1, 3)  # Randomly decides on secondary compass direction
    ram0 = r.randint(1, 4)
    ram1 = r.randint(1, 5)
    global rpathx
    global rpathy
    if maindir == 1: #North
        if secdir == 1: #NW
            rpathx = rpathx - ram0
            rpathy = rpathy + ram1
        if secdir == 2: #NN
            rpathy = rpathy + ram1
        if secdir == 3: #NE
            rpathx = rpathx + ram0
            rpathy = rpathy + ram1
    if maindir == 2: #East
        if secdir == 1:  # EN
            rpathy = rpathy + ram0
            rpathx = rpathx + ram1
        if secdir == 2:  # EE
            rpathx = rpathx + ram1
        if secdir == 3:  # ES
            rpathy = rpathy - ram0
            rpathx = rpathx + ram1
    if maindir == 3: #South
        if secdir == 1:  # SE
            rpathx = rpathx + ram0
            rpathy = rpathy - ram1
        if secdir == 2:  # SS
            rpathy = rpathy - ram1
        if secdir == 3:  # SW
            rpathx = rpathx - ram0
            rpathy = rpathy - ram1
    if maindir == 4: #West
        if secdir == 1:  # WS
            rpathy = rpathy - ram0
            rpathx = rpathx - ram1
        if secdir == 2:  # WW
            rpathx = rpathx - ram1
        if secdir == 3:  # WN
            rpathy = rpathy + ram0
            rpathx = rpathx - ram1
    cordgen.pathcord = (rpathx, rpathy)
    pix2la = round(abs((rpathy/ymax)*(botlat - toplat) + toplat), 4)
    pix2lo = round(((rpathx/xmax)*(rightlon - leftlon) + leftlon), 4)
    cordgen.pixcord = (pix2la, pix2lo)

def hudDisp(frame, name, data, nc, dc, rtl, rbr, bgr, thick, fs):
    #Display data with box around it
    #frame = frame to display on, name = name of data, data = data displayed after name
    #nc = name cords for text, dc = data cords for text
    #rtl = top left rect cords, rbr = bottom right rect cords
    #bgr = BGR values, thick = thickness of text, fs = font size
    cv2.putText(frame, name, nc, cv2.FONT_HERSHEY_SIMPLEX, fs, bgr, thick)
    cv2.rectangle(frame, rtl, rbr, bgr, thick)
    cv2.putText(frame, data, dc, cv2.FONT_HERSHEY_SIMPLEX, fs, bgr, thick)


hudstate = 0
armed = False

blinkc = 0
mrpix = [padx, pady]  # Recent pixel cords matrix
mrcord = [round(lp[0], 4), round(lp[1], 4)]  # Recent cords matrix

while True:
    time.sleep(0.05)#(0.05 is good)
    newsat = sat.copy()  # Draw on clone if it's temporary (cords, dots, etc)
    now = datetime.now()
    ct = now.strftime("%I:%M:%S %p")
    hudDisp(newsat, "", str(ct), (0, 0), (18, 40), (0, 0), (0, 0), (10, 10, 10), 2, 0.9)  # Time HUD
    cv2.line(newsat, (18, 50), (210, 50), (10, 10, 10), 3)  # Separation line
    cv2.rectangle(sat, (1, 1), (808, 809), (0, 0, 0), 2)  # Alignment Box
    cv2.circle(sat, (405, 405), 3, (0, 255, 0), 5)  # Launch pad location
    #Draw Compass
    cv2.line(sat, (30, 750), (90, 750), (10, 10, 10), 3) #Hori
    cv2.line(sat, (60, 720), (60, 780), (10, 10, 10), 3) #Vert
    cv2.putText(sat, "N", (55,714), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10,10,10), 2)
    cv2.putText(sat, "S", (54,796), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
    cv2.putText(sat, "E", (95,754), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
    cv2.putText(sat, "W", (14,754), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)

    if armed:
        cordgen()
        mrpix[0] = cordgen.pathcord[0]
        mrpix[1] = cordgen.pathcord[1]
        mrcord[0] = cordgen.pixcord[0]
        mrcord[1] = cordgen.pixcord[1]
        #Drawing HUD

    if hudstate == 0: #Decimal Degrees HUD
        hudDisp(newsat, "Lat:", str(mrcord[0]), (18, 78), (92, 78), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
        hudDisp(newsat, "Lon:", str(mrcord[1]), (18, 110), (75, 110), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
    if hudstate == 1: #Degrees Minutes HUD
        #Decimal degrees to Degrees minutes conversion
        dmla = str(math.floor(mrcord[0])) + " " + str(round((mrcord[0] % 1) * 60, 3))
        dmlo = str(math.ceil(mrcord[1])) + " " + str(abs(round((mrcord[1] % 1) * 60 - 60, 3)))
        #print(mrcord)
        #print(dmla,dmlo)
        hudDisp(newsat, "Lat:", str(dmla), (18, 78), (92, 78), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
        hudDisp(newsat, "Lon:", str(dmlo), (18, 110), (75, 110), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
    if hudstate == 2: #Distnace HUD
        disx = rpathx - padx
        disy = rpathy - pady
        try:
            deg = round((math.degrees(math.atan(disy/disx))))
        except ZeroDivisionError:
            deg = 0
        if disx < 0: #West
            dir2 = "W"
        else: #East
            dir2 = "E"
        if disy > 0 and dir2 == "E": #SE
            dir1 = "S"
            deg += 90
        elif disy > 0 and dir2 == "W": #SW
            dir1 = "S"
            deg += 270
        elif disy < 0 and dir2 == "E": #NE
            dir1 = "N"
            deg = 90 + deg
        elif disy < 0 and dir2 == "W": #NW
            dir1 = "N"
            deg += 270
        else:
            dir1 = "N"
        direct = str(deg) + " " + dir1 + dir2
        dist = round(math.sqrt((disx ** 2) + (disy ** 2)), 2)
        dist2mile = round((dist / padx * 3.2), 2)
        hudDisp(newsat, "Distance: ", str(str(dist2mile) + " mi"), (18, 78), (126, 78), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
        hudDisp(newsat, "Direction: ", direct, (18, 110), (126, 110), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
        cv2.line(newsat, (padx, pady), mrpix, (0, 240, 255), 3)  #Distance line
    if hudstate > 2:
        hudstate = 0

    #Drawing location dot
    cv2.circle(sat, mrpix, 1, (0, 120, 255), 5) #Tracked path
    cv2.circle(newsat, mrpix, 1, (0, 0, 255), 5) #Recent cords
    if blinkc % 10 < 5: #Blinking dot border
        cv2.circle(newsat, mrpix, 12, (0, 0, 255), 2)
        cv2.circle(newsat, mrpix, 2, (0, 0, 255), 5)
    blinkc += 1

    if armed is False:
        hudDisp(newsat, "Disarmed", "", (18, 142), (0, 0), (0, 0), (0, 0), (0, 10, 255), 2, 0.7)

    cv2.imshow(winName, newsat)

    if keyboard.is_pressed('h'):
        time.sleep(0.1)
        if keyboard.is_pressed('h') is False:
            hudstate += 1

    if keyboard.is_pressed('a'):
        time.sleep(0.1)
        if keyboard.is_pressed('a') is False:
            armed = not armed

    if cv2.waitKey(1) == 27:
        break
