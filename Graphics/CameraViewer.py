import sys

import matplotlib.pyplot as plt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from Graphics.Base_Classes_graphics.CameraViewer_GUI import Ui_PylonCamViewer
from Hardware.Detector import *


class CamViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.gui = Ui_PylonCamViewer()
        self.gui.setupUi(self)

        self.timer = QTimer(self)

        self.gui.StartGrab.clicked.connect(self.start_grab)

        self.gui.StopGrab.clicked.connect(self.stop_grab)

        self.gui.SetAcqTime.clicked.connect(self.SetAcqTime)  # Acquisition Time button
        self.camera = Camera()  # Switch to None for debugging
        self.canvas = FigureCanvas((plt.Figure()))
        # self.initUI()



    def start_grab(self):
        self.timer.timeout.connect(self.grab_data)
        self.timer.start(100)  # update every 100 ms

    def stop_grab(self):
        self.timer.stop()

    def grab_data(self):
        """
        switch to Pass for debugging
        :return:
        """
        data = self.camera.grabdata()  # this should already be a np object.
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.imshow(data)
        self.canvas.draw()

    def SetAcqTime(self):
        self.camera.MyExpTime = self.SetAcqTime.text()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CamViewer()
    window.show()
    sys.exit(app.exec_())
