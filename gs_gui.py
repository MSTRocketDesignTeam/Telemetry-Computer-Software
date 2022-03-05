import csv
import sys
import time
from datetime import date

import cv2
import pytz
from pytz import timezone
from datetime import datetime, timezone
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QImage, QPixmap

from pyqtgraph import PlotWidget
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


class RDT_GS_GUI(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('rdtGsRaw.ui', self)

        dateL = date.today().strftime("%m / %d / %Y")
        self.date.setText(dateL)

        self.worker = WorkerThread()
        self.worker.start()

        self.fname1 = None

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
        self.worker.up_Tracking.connect(self.upTracking)

        # Menu buttons
        self.actionData.triggered.connect(self.fileData)
        self.actionAvionics.triggered.connect(self.fileAvi)
        self.actionTelemetry.triggered.connect(self.fileTelem)
        self.actionTracking.triggered.connect(self.fileTrack)

        # Graphing

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

    # Obtain file source for all data values
    def fileData(self):
        global dataFile
        dataFile = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')[0]

    def fileAvi(self):
        global aviFile
        aviFile = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')[0]

    def fileTelem(self):
        global teleFile
        teleFile = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')[0]

    def fileTrack(self):
        global trackFile
        trackFile = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')[0]

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
    up_Tracker = pyqtSignal(QImage)

    c = True
    METstart = time.time()

    def run(self):
        sat = cv2.imread("imgs/sat3.PNG")
        while True:
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
                    xV = []
                    yV = []
                    for row in reader:
                        xV.append(row[0])
                        yV.append(row[1])
                        pass
                    self.up_Data.emit(str(row[1]) + " m",
                                      str(row[2]) + " m/s",
                                      str(row[3]) + " m/s\u00b2",
                                      str(row[4]) + " \u00B0/s")
            except:
                pass

            try:
                with open(aviFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_Avionics.emit(str(row[1]) + " V",
                                          str(row[2]) + " \u00B0C",
                                          str(row[3]) + " Hz",
                                          str(row[4]) + " %",
                                          str(row[5]) + " %",
                                          str(row[6]),
                                          str(row[7]))
            except:
                pass

            try:
                with open(teleFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_Telemetry.emit(str(row[1]),
                                           str(row[2]) + " m",
                                           str(row[3]) + " m/s",
                                           str(row[4]) + " dBm",
                                           str(row[5]),
                                           str(row[6]))
            except:
                pass

            try:
                with open(trackFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_Tracking.emit(str(round(float(row[1]), 6)),
                                          str(round(float(row[2]), 6)),
                                          str(row[3]) + " m",
                                          str(row[4]) + " \u00B0")
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
