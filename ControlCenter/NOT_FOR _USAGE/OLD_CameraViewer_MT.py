import matplotlib.pyplot as plt
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ControlCenter import Control_Utilities as cu
from Graphics.Base_Classes_graphics.CameraViewer_GUI import Ui_PylonCamViewer
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from Hardware.Detector import Camera
from ControlCenter.MultiThreading import *


class CamViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gui = Ui_PylonCamViewer()
        self.gui.setupUi(self)

        #Button Connection
        self.gui.StartGrab.clicked.connect(self.start_grab)
        self.gui.StopGrab.clicked.connect(self.stop_grab)
        self.gui.SetAcqTime.clicked.connect(self.setAcqTime)  # Acquisition Time button


        self.camera = Camera()  # Switch to None for debugging
        self.canvas = FigureCanvas(plt.figure())
        self.ax = self.canvas.figure.add_subplot(111)

        self.timer = QTimer()
        # self.timer.timeout.connect(self.update_plot)
        #self.timer.start(50)

        #self.worker_thread = None


        self.plot_layout = QVBoxLayout(self.gui.CamFrame)
        self.plot_layout.addWidget(self.canvas)
        # self.initUI()

    def start_grab(self):
        self.timer.start(100)  # update every 100 ms
        self.timer.timeout.connect(self.grab_data)

    def stop_grab(self):
        self.timer.stop()

    def handle_worker_error(self, message):
        self.show_warning(title="Error!", message=message)

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
            image = self.camera.frame
            if self.gui.FWHM_checkBox.isChecked():
                self.display_fwhm(image)

            if self.gui.centroid_checkBox.isChecked():
                self.display_centroid(image)


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

    def display_fwhm(self, nparray2D):
        fwhm_X, fwhm_Y = cu.MathUtils.calc_2D_fwhm(nparray2D)
        fwhm_X = round((2.74 * fwhm_X), 2)
        fwhm_Y = round((2.74 * fwhm_Y), 2)
        self.gui.FWHMX_label.setText(str(fwhm_X))
        self.gui.FWHMY_label.setText(str(fwhm_Y))

    def display_centroid(self, nparray2D):
        centroid = cu.MathUtils.centroid(nparray2D)
        #centroidX = centroid[1], centroidY = centroid[0]
        self.gui.centroidX_label.setText(str(centroid[1]))
        self.gui.centroidY_label.setText(str(centroid[0]))

    def on_grab_finished(self):
        self.gui.StopGrab.setEnabled(False)
        self.gui.StartGrab.setEnabled(True)

    def show_warning(self, title, message):
        warning = myWarningBox(
            title=title,
            message=message,
            parent=self
        )
        warning.show_warning()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CamViewer()
    window.show()
    sys.exit(app.exec_())