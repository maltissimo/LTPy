import sys

import matplotlib.pyplot as plt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from Graphics.Base_Classes_graphics.CameraViewer_GUI import Ui_PylonCamViewer
from Hardware.Detector import Camera


class CamViewer(QMainWindow):
    def __init__(self, camera_timer: QTimer):
        super().__init__()

        self.gui = Ui_PylonCamViewer()
        self.gui.setupUi(self)

        self.timer = camera_timer
        """self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)"""

        self.gui.StartGrab.clicked.connect(self.start_grab)

        self.gui.StopGrab.clicked.connect(self.stop_grab)

        self.gui.SetAcqTime.clicked.connect(self.setAcqTime)  # Acquisition Time button
        self.camera = Camera()  # Switch to None for debugging
        self.canvas = FigureCanvas(plt.figure())
        self.ax = self.canvas.figure.add_subplot(111)


        self.plot_layout = QVBoxLayout(self.gui.CamViewer)
        self.plot_layout.addWidget(self.canvas)
        # self.initUI()



    def start_grab(self):
        #self.timer.start(100) # update every 100 ms
        self.timer.timeout.connect(self.grab_data)


    def stop_grab(self):
        self.timer.stop()

    def grab_data(self):
        """
        switch to Pass for debugging
        :return:
        """
        self.camera.grabdata()
        if self.camera.frame is not None:
            """print(f"frame type: {type(self.camera.frame)}")
            print(f"frame shape: {self.camera.frame.shape}")"""
            self.ax.clear()
            self.ax.imshow(self.camera.frame)
            self.plot_center_mark()
            self.ax.grid(True)
            self.canvas.draw()

    def setAcqTime(self):
        newtime = float(self.gui.AcqTLineEdit.text())
        self.camera.set_exp_time(newtime)

    def plot_center_mark(self):
        x_lim = self.ax.get_xlim()
        y_lim = self.ax.get_ylim()

        x_center =(x_lim[0] + x_lim[1])/2
        y_center = (y_lim[0] + y_lim[1])/2

        self.ax.scatter(x_center, y_center, color ='red', marker ="+", s = 100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CamViewer()
    window.show()
    sys.exit(app.exec_())
