import matplotlib.pyplot as plt
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
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

        self.worker_thread = None


        self.plot_layout = QVBoxLayout(self.gui.CamViewer)
        self.plot_layout.addWidget(self.canvas)
        # self.initUI()

    def start_grab(self):
        if self.worker_thread is None:
            self.worker_thread = WorkerThread(self.grab_data)

            self.worker_thread.update_signal.connect(self.grab_data)
            self.worker_thread.error_signal.connect(self.handle_worker_error)
            self.worker_thread.end_signal.connect(self.on_grab_finished)

            self.worker_thread.start()

            self.gui.StartGrab.setEnabled(False)
            self.gui.StopGrab.setEnabled(True)

    def stop_grab(self):
        if self.worker_thread:
            self.worker_thread.stop()
            self.worker_thread = None

            self.gui.StartGrab.setEnabled(True)
            self.gui.StopGrab.setEnabled(False)

    def handle_worker_error(self, message):
        self.show_warning(title="Error!", message=message)

    @synchronized_method
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
            if self.gui.checkBox.isChecked():

                image = self.camera.frame
                self.display_fwhm(image)

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

    @synchronized_method
    def display_fwhm(self, nparray2D):
        fwhm_X, fwhm_Y = cu.MathUtils.calc_2D_fwhm(nparray2D)
        self.gui.FWHMX_label.setText(str(2.74* fwhm_X))
        self.gui.FWHMY_label.setText(str(2.74 * fwhm_Y))

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
