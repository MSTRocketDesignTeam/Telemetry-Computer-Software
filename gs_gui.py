import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QImage
from rawGuiSetup import Ui_MainWindow
from trackerOnly import *
import trackerOnly

class updateUI(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.trackerF()

    def trackerF(self):
        hudstate = 0
        armed = True
        blinkc = 0
        mrpix = [padx, pady]  # Recent pixel cords matrix
        mrcord = [round(lp[0], 4), round(lp[1], 4)]  # Recent cords matrix
        #time.sleep(0.05)  # (0.05 is good)
        newsat = sat.copy()  # Draw on clone if it's temporary (cords, dots, etc)
        now = datetime.now()
        ct = now.strftime("%I:%M:%S %p")
        hudDisp(newsat, "", str(ct), (0, 0), (18, 40), (0, 0), (0, 0), (10, 10, 10), 2, 0.9)  # Time HUD
        cv2.line(newsat, (18, 50), (210, 50), (10, 10, 10), 3)  # Separation line
        cv2.rectangle(sat, (1, 1), (808, 809), (0, 0, 0), 2)  # Alignment Box
        cv2.circle(sat, (405, 405), 3, (0, 255, 0), 5)  # Launch pad location
        # Draw Compass
        cv2.line(sat, (30, 750), (90, 750), (10, 10, 10), 3)  # Hori
        cv2.line(sat, (60, 720), (60, 780), (10, 10, 10), 3)  # Vert
        cv2.putText(sat, "N", (55, 714), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
        cv2.putText(sat, "S", (54, 796), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
        cv2.putText(sat, "E", (95, 754), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
        cv2.putText(sat, "W", (14, 754), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)

        if armed:
            cordgen()
            mrpix[0] = cordgen.pathcord[0]
            mrpix[1] = cordgen.pathcord[1]
            mrcord[0] = cordgen.pixcord[0]
            mrcord[1] = cordgen.pixcord[1]
            # Drawing HUD
        if hudstate == 0:  # Decimal Degrees HUD
            hudDisp(newsat, "Lat:", str(mrcord[0]), (18, 78), (92, 78), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
            hudDisp(newsat, "Lon:", str(mrcord[1]), (18, 110), (75, 110), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
            self.ui.LonCord.setText(str(mrcord[0]))
            self.ui.LonCord.setText(str(mrcord[1]))
        if hudstate == 1:  # Degrees Minutes HUD
            # Decimal degrees to Degrees minutes conversion
            dmla = str(math.floor(mrcord[0])) + " " + str(round((mrcord[0] % 1) * 60, 3))
            dmlo = str(math.ceil(mrcord[1])) + " " + str(abs(round((mrcord[1] % 1) * 60 - 60, 3)))
            self.ui.LatCord.setText(str(mrcord[0]))
            self.ui.LonCord.setText(str(mrcord[1]))
            hudDisp(newsat, "Lat:", str(dmla), (18, 78), (92, 78), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
            hudDisp(newsat, "Lon:", str(dmlo), (18, 110), (75, 110), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
        if hudstate == 2:  # Distnace HUD
            disx = rpathx - padx
            disy = rpathy - pady
            try:
                deg = round((math.degrees(math.atan(disy / disx))))
            except ZeroDivisionError:
                deg = 0
            if disx < 0:  # West
                dir2 = "W"
            else:  # East
                dir2 = "E"
            if disy > 0 and dir2 == "E":  # SE
                dir1 = "S"
                deg += 90
            elif disy > 0 and dir2 == "W":  # SW
                dir1 = "S"
                deg += 270
            elif disy < 0 and dir2 == "E":  # NE
                dir1 = "N"
                deg = 90 + deg
            elif disy < 0 and dir2 == "W":  # NW
                dir1 = "N"
                deg += 270
            else:
                dir1 = "N"
            direct = str(deg) + " " + dir1 + dir2
            dist = round(math.sqrt((disx ** 2) + (disy ** 2)), 2)
            dist2mile = round((dist / padx * 3.2), 2)
            hudDisp(newsat, "Distance: ", str(str(dist2mile) + " mi"), (18, 78), (126, 78), (0, 0), (0, 0),
                    (255, 200, 0), 2, 0.70)
            hudDisp(newsat, "Direction: ", direct, (18, 110), (126, 110), (0, 0), (0, 0), (255, 200, 0), 2, 0.70)
            cv2.line(newsat, (padx, pady), mrpix, (0, 240, 255), 3)  # Distance line
        if hudstate > 2:
            hudstate = 0

        # Drawing location dot
        cv2.circle(sat, mrpix, 1, (0, 120, 255), 5)  # Tracked path
        cv2.circle(newsat, mrpix, 1, (0, 0, 255), 5)  # Recent cords
        if blinkc % 10 < 5:  # Blinking dot border
            cv2.circle(newsat, mrpix, 12, (0, 0, 255), 2)
            cv2.circle(newsat, mrpix, 2, (0, 0, 255), 5)
        blinkc += 1

        if armed is False:
            hudDisp(newsat, "Disarmed", "", (18, 142), (0, 0), (0, 0), (0, 0), (0, 10, 255), 2, 0.7)

        if keyboard.is_pressed('h'):
            time.sleep(0.1)
            if keyboard.is_pressed('h') is False:
                hudstate += 1

        if keyboard.is_pressed('a'):
            time.sleep(0.1)
            if keyboard.is_pressed('a') is False:
                armed = not armed

        im2qt = QImage(newsat,newsat.shape[1],newsat.shape[0],newsat.strides[0],QImage.Format_BGR888)
        self.tracker.setPixmap(QtGui.QPixmap(im2qt))

def setUpWindow():
    app = QtWidgets.QApplication(sys.argv)
    ex = Ui_MainWindow()
    w = QtWidgets.QMainWindow()
    ex.setupUi(w)
    w.show()
    sys.exit(app.exec_())
