import csv
import sys
import time
from datetime import date

import cv2
import imutils
import pytz
from pytz import timezone
from datetime import datetime, timezone
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QImage, QPixmap

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

import trackerOnly
from trackerOnly import *

from PyQt5.QtWidgets import *

class RDT_GS_GUI(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('rdtGsRaw.ui', self)

        dateL = date.today().strftime("%m / %d / %Y")
        self.date.setText(dateL)

        self.worker = WorkerThread()
        self.worker.start()

        # Module Status updates
        self.worker.up_Module.connect(self.upModule)

        # Data updates
        self.worker.up_Data.connect(self.upData)
        self.worker.up_Data2.connect(self.upData2)

        # Avionics updates
        self.worker.up_Avionics.connect(self.upAvionics)

        # Telemetry updates
        self.worker.up_Telemetry.connect(self.upTelemetry)

        # Tracker updates
        #self.worker.up_Tracking.connect(self.upTracking)
        self.worker.up_TrackingTest.connect(self.upTrackingTest)
        self.armBut.clicked.connect(self.upArm)
        self.worker.up_Tracker.connect(self.upTracker)

        # Graphing
        self.worker.up_GraphData.connect(self.drawGraphs)
        self.velG.setLabel('bottom', 'Time (s)')
        self.velG.setLabel('left', 'Velocity (m/s)')
        self.velG.setTitle("Velocity", pen=pg.mkPen('k', width=2))
        self.velG.showGrid(x=True, y=True)
        self.velG.setBackground('DCDCDC')
        self.velG.getAxis('left').setTextPen('k')
        self.velG.getAxis('bottom').setTextPen('k')

        self.allaltG.setLabel('bottom', 'Time (s)')
        self.allaltG.setLabel('left', 'Altitude (m)')
        self.allaltG.setTitle("Altitude", pen=pg.mkPen('k', width=2))
        self.allaltG.showGrid(x=True, y=True)
        self.allaltG.setBackground('DCDCDC')
        self.allaltG.getAxis('left').setTextPen('k')
        self.allaltG.getAxis('bottom').setTextPen('k')
        self.allaltG.addLegend()

        self.allaccG.setLabel('bottom', 'Time (s)')
        self.allaccG.setLabel('left', 'Acceleration (m/s\u00b2)')
        self.allaccG.setTitle("Acceleration")
        self.allaccG.showGrid(x=True, y=True)
        self.allaccG.setBackground('DCDCDC')
        self.allaccG.getAxis('left').setTextPen('k')
        self.allaccG.getAxis('bottom').setTextPen('k')

        self.allorientG.setLabel('bottom', 'Time (s)')
        self.allorientG.setLabel('left', 'Roll Rate (\u00B0/s)')
        self.allorientG.setTitle("Roll Rate")
        self.allorientG.showGrid(x=True, y=True)
        self.allorientG.setBackground('DCDCDC')
        self.allorientG.getAxis('left').setTextPen('k')
        self.allorientG.getAxis('bottom').setTextPen('k')

        # Menu buttons
        self.actionData.triggered.connect(self.fileData)
        self.actionAvionics.triggered.connect(self.fileAvi)
        self.actionTelemetry.triggered.connect(self.fileTelem)
        self.actionTracking.triggered.connect(self.fileTrack)

    # Graphs
    def drawGraphs(self, timeD, yalt, yalt2, yaltav, yvel, yacc, yrollr):
        timeD = list(map(int, timeD))
        yalt = list(map(int, yalt))
        yalt2 = list(map(int, yalt2))
        yaltav = list(map(int, yaltav))
        yvel = list(map(int, yvel))
        yacc = list(map(int, yacc))
        yrollr = list(map(int, yrollr))

        self.velG.clear()
        self.velG.plot(timeD,yvel,pen=pg.mkPen('k', width=2))

        self.allaccG.clear()
        self.allaccG.plot(timeD, yacc, pen=pg.mkPen('k', width=2))

        self.allorientG.clear()
        self.allorientG.plot(timeD, yrollr, pen=pg.mkPen('k', width=2))

        self.allaltG.clear()
        self.allaltG.plot(timeD, yalt, pen=pg.mkPen('r', width=2), name='Barometer 1')
        self.allaltG.plot(timeD, yalt2, pen=pg.mkPen('b', width=2), name='Barometer 2')
        self.allaltG.plot(timeD, yaltav, pen=pg.mkPen('k', width=2), name='Average')

    # Module Status
    def upModule(self, dataacq, telemst, power, pyro):
        self.dataacqst.setText(dataacq)
        self.telemst.setText(telemst)
        self.powst.setText(power)
        self.pyrost.setText(pyro)

    # Data
    def upData(self, alt, vel, accel, rollr):
        self.altitude.setText(alt)
        self.velocity.setText(vel)
        self.acceleration.setText(accel)
        self.rollrate.setText(rollr)

    def upData2(self, timeL, UTC, MET):
        self.loctime.setText(timeL)
        self.utctime.setText(UTC)
        self.met.setText(MET)

    # Avionics
    def upAvionics(self, batv, batc, datar, dataer, onbds, chrg1, chrg2):
        self.batvolt.setText(batv)
        self.batemp.setText(batc)
        self.datarate.setText(datar)
        self.dataerror.setText(dataer)
        self.datastor.setText(onbds)
        self.charge1con.setText(chrg1)
        self.charge2con.setText(chrg2)

    # Telemetry
    def upTelemetry(self, gnss, posunc, velunc, sig, sentr, gnssst):
        self.gnsscount.setText(gnss)
        self.posunc.setText(posunc)
        self.velunc.setText(velunc)
        self.signal.setText(sig)
        self.sentrx.setText(sentr)
        self.gnssstatus.setText(gnssst)

    # Tracking
    def upTracking(self, lat, long, dist, direc):
        self.latcord.setText(lat)
        self.longcord.setText(long)
        self.dist.setText(dist)
        self.direc.setText(direc)

    def upTrackingTest(self, lat, long, dist, direc):
        self.latcord.setText(str(lat))
        self.longcord.setText(str(long))
        self.dist.setText(str(dist))
        self.direc.setText(direc)

    def upTracker(self, image):
        self.trackerimg.setPixmap(QPixmap.fromImage(image))

    def upArm(self):
        if self.worker.armed:
            self.armBut.setStyleSheet('background-color: red')
            self.armBut.setText("Disarm")
            self.worker.armed = False
        else:
            self.armBut.setStyleSheet('background-color: green')
            self.armBut.setText("Arm")
            self.worker.armed = True

    # Obtain file source for all data values
    def fileData(self):
        global dataFile
        dataFile = QFileDialog.getOpenFileName(self, 'Open File: Data', '', 'CSV Files (*.csv)')[0]

    def fileAvi(self):
        global aviFile
        aviFile = QFileDialog.getOpenFileName(self, 'Open File: Avionics', '', 'CSV Files (*.csv)')[0]

    def fileTelem(self):
        global teleFile
        teleFile = QFileDialog.getOpenFileName(self, 'Open File: Telemetry', '', 'CSV Files (*.csv)')[0]

    def fileTrack(self):
        global trackFile
        trackFile = QFileDialog.getOpenFileName(self, 'Open File: Tracking', '', 'CSV Files (*.csv)')[0]

class WorkerThread(QThread):
    # Module Status
    up_Module = pyqtSignal(str, str, str, str)

    # Data
    up_Data = pyqtSignal(str, str, str, str)
    up_Data2 = pyqtSignal(str, str, str)

    # Avionics
    up_Avionics = pyqtSignal(str, str, str, str, str, str, str)

    # Telemetry
    up_Telemetry = pyqtSignal(str, str, str, str, str, str)

    # Tracker
    up_Tracking = pyqtSignal(str, str, str, str)
    up_TrackingTest = pyqtSignal(float, float, float, str)
    up_Arming = pyqtSignal(bool)

    up_Tracker = pyqtSignal(QImage)

    # Graphing
    up_GraphData = pyqtSignal(list, list, list, list, list, list, list)

    METstart = time.time()

    c = True
    armed = False
    blinkc = 0
    mrpix = [padx, pady]  # Recent pixel cords matrix
    mrcord = [round(lp[0], 4), round(lp[1], 4)]  # Recent cords matrix

    def run(self):
        while True:
            print(self.armed)
            newsat = sat.copy()
            # Draw Compass
            cv2.line(sat, (30, 750), (90, 750), (10, 10, 10), 3)  # Hori
            cv2.line(sat, (60, 720), (60, 780), (10, 10, 10), 3)  # Vert
            cv2.putText(sat, "N", (55, 714), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
            cv2.putText(sat, "S", (54, 796), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
            cv2.putText(sat, "E", (95, 754), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)
            cv2.putText(sat, "W", (14, 754), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 2)

            if self.armed:
                self.mrpix[0] += 1
                self.mrpix[1] += 1
                self.mrcord[0] += 0.01
                self.mrcord[1] += 0.01

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
            dist2meters = dist2mile * 1609.34
            cv2.line(newsat, (padx, pady), mrpix, (0, 240, 255), 3)  # Distance line

            # Drawing location dot
            cv2.circle(sat, (405, 405), 3, (0, 255, 0), 5) #Launch Pad Location
            cv2.circle(sat, mrpix, 1, (0, 120, 255), 5)  # Tracked path
            cv2.circle(newsat, mrpix, 1, (0, 0, 255), 5)  # Recent cords
            if self.blinkc % 10 < 5:  # Blinking dot border
                cv2.circle(newsat, mrpix, 12, (0, 0, 255), 2)
                cv2.circle(newsat, mrpix, 2, (0, 0, 255), 5)
            self.blinkc += 1

            self.up_TrackingTest.emit(mrcord[0], mrcord[1], dist2meters, direct)

            image = imutils.resize(newsat,width=357)
            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
            self.up_Tracker.emit(image)

            if self.c:
                dataacqst = "Active"
                telemst = "Active"
                power = "Active"
                pyro = "Active"
            else:
                dataacqst = "Inactive"
                telemst = "Inactive"
                power = "Inactive"
                pyro = "Inactive"

            self.up_Module.emit(dataacqst, telemst, power, pyro)


            try:
                with open(dataFile, "r") as file:
                    reader = csv.reader(file)
                    timeD = []
                    yAlt = []
                    yAlt2 = []
                    yAltAv = []
                    yVel = []
                    yAcc = []
                    yRollr = []
                    next(file)
                    for row in reader:
                        timeD.append(row[0])
                        yAlt.append(row[1])
                        yAlt2.append(row[2])
                        altav = round((int(row[1]) + int(row[2]))/2)
                        yAltAv.append(str(altav))
                        yVel.append(row[3])
                        yAcc.append(row[4])
                        yRollr.append(row[5])
                        pass
                    self.up_Data.emit(yAltAv[-1] + " m",
                                      row[3] + " m/s",
                                      row[4] + " m/s\u00b2",
                                      row[5] + " \u00B0/s")
                    self.up_GraphData.emit(timeD, yAlt, yAlt2, yAltAv, yVel, yAcc, yRollr)
            except:
                pass

            try:
                with open(aviFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_Avionics.emit(row[1] + " V",
                                          row[2] + " \u00B0C",
                                          row[3] + " Hz",
                                          row[4] + " %",
                                          row[5] + " %",
                                          row[6],
                                          row[7])
            except:
                pass

            try:
                with open(teleFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_Telemetry.emit(row[1],
                                           row[2] + " m",
                                           row[3] + " m/s",
                                           row[4] + " dBm",
                                           row[5],
                                           row[6])
            except:
                pass

            try:
                with open(trackFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_Tracking.emit(str(round(float(row[1]), 6)),
                                          str(round(float(row[2]), 6)),
                                          row[3] + " m",
                                          row[4] + " \u00B0")
            except:
                pass

            timeNOW = datetime.now(pytz.timezone('US/Central'))
            timeL = timeNOW.strftime("%I:%M:%S %Z")

            utcNOW = datetime.now(timezone.utc)
            utcL = utcNOW.strftime("%I:%M:%S %Z")

            METnew = time.time()
            metdif = METnew - self.METstart
            mins = metdif // 60
            sec = round((metdif % 60))
            hours = mins // 60
            mins = mins % 60
            METl = "{:02d}:{:02d}:{:02d}".format(int(hours), int(mins), sec)

            self.up_Data2.emit(timeL, utcL, str(METl))

            self.c = not self.c
            time.sleep(0.1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = RDT_GS_GUI()
    mainWindow.show()
    sys.exit(app.exec_())
