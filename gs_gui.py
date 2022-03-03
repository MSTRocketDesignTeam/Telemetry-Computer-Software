import csv
import sys
import time
from datetime import datetime, date, timezone
import datetime

import pytz
from pytz import timezone
from datetime import datetime, timezone
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# from rawGuiSetup import Ui_MainWindow
import cv2

import keyboard
import math
import random as r
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

class RDT_GS_GUI(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('qtdesignerRaw.ui', self)

        dateL = date.today().strftime("%m / %d / %Y")
        self.date.setText(dateL)

        self.worker = WorkerThread()
        self.worker.start()

        self.worker.up_dataacqst.connect(self.upData)
        self.worker.up_telemst.connect(self.upTelem)
        self.worker.up_power.connect(self.upPow)
        self.worker.up_pyro.connect(self.upPyro)
        self.worker.up_time.connect(self.upTime)
        self.worker.up_MET.connect(self.upMET)
        self.worker.up_UTC.connect(self.upUTC)

        self.actionData.triggered.connect(self.fileData)
        self.actionModule_Status.triggered.connect(self.fileMS)
        self.actionAvionics.triggered.connect(self.fileAvi)
        self.actionTelemetry.triggered.connect(self.fileTelem)
        self.actionTracking.triggered.connect(self.fileTrack)

    def upData(self, dataacq):
        self.dataacqst.setText(dataacq)

    def upTelem(self, telemst):
        self.telemst.setText(telemst)

    def upPow(self, power):
        self.powst.setText(power)

    def upPyro(self, pyro):
        self.pyrost.setText(pyro)

    def upTime(self, timeL):
        self.loctime.setText(timeL)

    def upMET(self, MET):
        self.met.setText(MET)

    def upUTC(self, UTC):
        self.utctime.setText(UTC)

    def fileData(self):
        fname1 = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')
        return fname1[0]

    def fileMS(self):
        fname2 = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')

    def fileAvi(self):
        fname3 = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')

    def fileTelem(self):
        fname4 = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')

    def fileTrack(self):
        fname5 = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv)')

class WorkerThread(QThread):
    up_dataacqst = pyqtSignal(str)
    up_telemst = pyqtSignal(str)
    up_power = pyqtSignal(str)
    up_pyro = pyqtSignal(str)

    up_time = pyqtSignal(str)
    up_MET = pyqtSignal(str)
    up_UTC = pyqtSignal(str)

    c = True
    METstart = time.time()

    def run(self):
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

            self.up_dataacqst.emit(dataacqst)
            self.up_telemst.emit(telemst)
            self.up_power.emit(power)
            self.up_pyro.emit(pyro)

            with open('dataFiles/dataF.csv') as file:
                reader = csv.reader(file)
                for row in reader:
                    print(row)

            timeNOW = datetime.now(pytz.timezone('US/Central'))
            timeL = timeNOW.strftime("%I:%M:%S %Z")
            self.up_time.emit(timeL)

            utcNOW = datetime.now(timezone.utc)
            utcL = utcNOW.strftime("%I:%M:%S %Z")
            self.up_UTC.emit(utcL)

            METnew = time.time()
            metdif = METnew - self.METstart
            mins = metdif // 60
            sec = round((metdif % 60))
            hours = mins // 60
            mins = mins % 60
            METl = "{:02d}:{:02d}:{:02d}".format(int(hours), int(mins), sec)
            self.up_MET.emit(str(METl))

            self.c = not self.c
            time.sleep(0.1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = RDT_GS_GUI()
    mainWindow.show()
    sys.exit(app.exec_())
