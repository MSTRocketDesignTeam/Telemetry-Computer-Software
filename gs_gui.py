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
from PyQt5.QtWidgets import QApplication, QWidget
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

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

        self.fname1 = None

        # Module Status updates
        self.worker.up_dataacqst.connect(self.upData)
        self.worker.up_telemst.connect(self.upTelem)
        self.worker.up_power.connect(self.upPow)
        self.worker.up_pyro.connect(self.upPyro)

        # Data updates
        self.worker.up_time.connect(self.upTime)
        self.worker.up_MET.connect(self.upMET)
        self.worker.up_UTC.connect(self.upUTC)
        self.worker.up_alt.connect(self.upAlt)
        self.worker.up_vel.connect(self.upVel)
        self.worker.up_accel.connect(self.upAccel)
        self.worker.up_rollr.connect(self.upRollr)

        # Avionics updates
        self.worker.up_batV.connect(self.upBatv)
        self.worker.up_batT.connect(self.upBatc)
        self.worker.up_dataR.connect(self.upDatar)
        self.worker.up_dataER.connect(self.upDataer)
        self.worker.up_onbDS.connect(self.upOnbds)
        self.worker.up_chrg1.connect(self.upChrg1)
        self.worker.up_chrg2.connect(self.upChrg2)

        # Telemetry updates
        self.worker.up_gnss.connect(self.upGnss)
        self.worker.up_posunc.connect(self.upPosunc)
        self.worker.up_velunc.connect(self.upVelunc)
        self.worker.up_signal.connect(self.upSignal)
        self.worker.up_sentr.connect(self.upSentr)
        self.worker.up_gnssSt.connect(self.upGnssSt)

        # Tracker updates
        self.worker.up_lat.connect(self.upLat)
        self.worker.up_long.connect(self.upLong)
        self.worker.up_dist.connect(self.upDist)
        self.worker.up_direc.connect(self.upDirec)

        # Menu buttons
        self.actionData.triggered.connect(self.fileData)
        self.actionAvionics.triggered.connect(self.fileAvi)
        self.actionTelemetry.triggered.connect(self.fileTelem)
        self.actionTracking.triggered.connect(self.fileTrack)

    # Module Status
    def upData(self, dataacq):
        self.dataacqst.setText(dataacq)

    def upTelem(self, telemst):
        self.telemst.setText(telemst)

    def upPow(self, power):
        self.powst.setText(power)

    def upPyro(self, pyro):
        self.pyrost.setText(pyro)

    # Data
    def upTime(self, timeL):
        self.loctime.setText(timeL)

    def upMET(self, MET):
        self.met.setText(MET)

    def upUTC(self, UTC):
        self.utctime.setText(UTC)

    def upAlt(self, alt):
        self.altitude.setText(alt)

    def upVel(self, vel):
        self.velocity.setText(vel)

    def upAccel(self, accel):
        self.acceleration.setText(accel)

    def upRollr(self, rollr):
        self.rollrate.setText(rollr)

    # Avionics
    def upBatv(self, batv):
        self.batvolt.setText(batv)

    def upBatc(self, batc):
        self.batemp.setText(batc)

    def upDatar(self, datar):
        self.datarate.setText(datar)

    def upDataer(self, dataer):
        self.dataerror.setText(dataer)

    def upOnbds(self, onbds):
        self.datastor.setText(onbds)

    def upChrg1(self, chrg1):
        self.charge1con.setText(chrg1)

    def upChrg2(self, chrg2):
        self.charge2con.setText(chrg2)

    # Telemetry
    def upGnss(self, gnss):
        self.gnsscount.setText(gnss)

    def upPosunc(self, posunc):
        self.posunc.setText(posunc)

    def upVelunc(self, velunc):
        self.velunc.setText(velunc)

    def upSignal(self, sig):
        self.signal.setText(sig)

    def upSentr(self, sentr):
        self.sentrx.setText(sentr)

    def upGnssSt(self, gnssst):
        self.gnssstatus.setText(gnssst)

    # Tracking
    def upLat(self, lat):
        self.latcord.setText(lat)

    def upLong(self, long):
        self.longcord.setText(long)

    def upDist(self, dist):
        self.dist.setText(dist)

    def upDirec(self, direc):
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
    up_dataacqst = pyqtSignal(str)
    up_telemst = pyqtSignal(str)
    up_power = pyqtSignal(str)
    up_pyro = pyqtSignal(str)

    # Data
    up_time = pyqtSignal(str)
    up_MET = pyqtSignal(str)
    up_UTC = pyqtSignal(str)
    up_alt = pyqtSignal(str)
    up_vel = pyqtSignal(str)
    up_accel = pyqtSignal(str)
    up_rollr = pyqtSignal(str)

    # Avionics
    up_batV = pyqtSignal(str)
    up_batT = pyqtSignal(str)
    up_dataR = pyqtSignal(str)
    up_dataER = pyqtSignal(str)
    up_onbDS = pyqtSignal(str)
    up_chrg1 = pyqtSignal(str)
    up_chrg2 = pyqtSignal(str)

    # Telemetry
    up_gnss = pyqtSignal(str)
    up_posunc = pyqtSignal(str)
    up_velunc = pyqtSignal(str)
    up_signal = pyqtSignal(str)
    up_sentr = pyqtSignal(str)
    up_gnssSt = pyqtSignal(str)

    # Tracker
    up_lat = pyqtSignal(str)
    up_long = pyqtSignal(str)
    up_dist = pyqtSignal(str)
    up_direc = pyqtSignal(str)
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

            self.up_dataacqst.emit(dataacqst)
            self.up_telemst.emit(telemst)
            self.up_power.emit(power)
            self.up_pyro.emit(pyro)

            try:
                with open(dataFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_alt.emit(str(row[1]) + " m")
                    self.up_vel.emit(str(row[2]) + " m/s")
                    self.up_accel.emit(str(row[3]) + " m/s\u00b2")
                    self.up_rollr.emit(str(row[4]) + " \u00B0/s")
            except:
                pass

            try:
                with open(aviFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_batV.emit(str(row[1]) + " V")
                    self.up_batT.emit(str(row[2]) + " \u00B0C")
                    self.up_dataR.emit(str(row[3]) + " Hz")
                    self.up_dataER.emit(str(row[4]) + " %")
                    self.up_onbDS.emit(str(row[5]) + " %")
                    self.up_chrg1.emit(str(row[6]))
                    self.up_chrg2 .emit(str(row[7]))
            except:
                pass

            try:
                with open(teleFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_gnss.emit(str(row[1]))
                    self.up_posunc.emit(str(row[2]) + " m")
                    self.up_velunc.emit(str(row[3]) + " m/s")
                    self.up_signal.emit(str(row[4]) + " dBm")
                    self.up_sentr.emit(str(row[5]))
                    self.up_gnssSt.emit(str(row[6]))
            except:
                pass

            try:
                with open(trackFile, "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        pass
                    self.up_lat.emit(str(round(float(row[1]), 6)))
                    self.up_long.emit(str(round(float(row[2]), 6)))
                    self.up_dist.emit(str(row[3]) + " m")
                    self.up_direc.emit(str(row[4]) + " \u00B0")
            except:
                pass

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
