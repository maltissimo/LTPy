import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

import ControlCenter.MathUtils
from ControlCenter import Control_Utilities as cu
from Graphics.Base_Classes_graphics.CameraViewer_GUI import Ui_PylonCamViewer
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from Hardware.Detector import Camera


class CamViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gui = Ui_PylonCamViewer()
        self.gui.setupUi(self)

        # Button Connections
        self.gui.StartGrab.clicked.connect(self.start_grab)
        self.gui.StopGrab.clicked.connect(self.stop_grab)
        self.gui.SetAcqTime.clicked.connect(self.setAcqTime)

        self.camera = Camera()
        self.running = False

        self.plot_layout = QVBoxLayout(self.gui.CamFrame)
        self.display_label = QLabel()
        self.plot_layout.addWidget(self.display_label)

        self.gui.StartGrab.setEnabled(True)
        self.gui.StopGrab.setEnabled(False)

    def start_grab(self):
        """self.timer.start(100)  # Update every 100 ms
        self.timer.timeout.connect(self.grab_data)"""
        if not self.running:
            self.running = True
            self.gui.StartGrab.setEnabled(False)
            self.gui.StopGrab.setEnabled(True)
            self.update_plot()

    def update_plot(self):
        if not self.running:
            return
        self.grab_data()
        QTimer.singleShot(50, self.update_plot)

    def stop_grab(self):
        # self.timer.stop()
        self.running = False
        self.gui.StartGrab.setEnabled(True)
        self.gui.StopGrab.setEnabled(False)
    def grab_data(self):
        self.camera.grabdata()
        if self.camera.frame is not None:
            image = self.camera.frame

            if self.gui.FWHM_checkBox.isChecked():
                self.display_fwhm(image)

            if self.gui.centroid_checkBox.isChecked():
                self.display_centroid(image)

            self.plot_center_mark(image)
            self.display_image(image)

    def setAcqTime(self):
        newtime = float(self.gui.AcqTLineEdit.text())
        self.camera.set_exp_time(newtime)

    def plot_center_mark(self, image):
        #print("image.shape : ", image.shape)
        height = image.shape[0]
        width = image.shape[1]
        center_x = width // 2
        center_y = height // 2

        # Draw a red cross at the center
        cv2.drawMarker(image, (center_x, center_y), (255, 255, 255), markerType=cv2.MARKER_CROSS, markerSize=80,
                       thickness=10)

    def display_fwhm(self, nparray2D):
        fwhm_X, fwhm_Y = ControlCenter.MathUtils.MathUtils.calc_2D_fwhm(nparray2D)
        fwhm_X = round((2.74 * fwhm_X), 2)
        fwhm_Y = round((2.74 * fwhm_Y), 2)
        self.gui.FWHMX_label.setText(str(fwhm_X))
        self.gui.FWHMY_label.setText(str(fwhm_Y))

    def display_centroid(self, nparray2D):
        centroid = ControlCenter.MathUtils.MathUtils.centroid(nparray2D)
        self.gui.centroidX_label.setText(str(centroid[1]))
        self.gui.centroidY_label.setText(str(centroid[0]))

    def add_grid(self, image):
        """
        Adds a grid to the image by drawing horizontal and vertical lines.
        """
        height, width = image.shape
        grid_color = (255, 255, 255)  # Green color for grid lines (BGR format)
        line_thickness = 4  # Line thickness

        # Define grid spacing
        grid_spacing = 1000  # Adjust as needed for your image resolution

        # Draw horizontal lines
        for y in range(0, height, grid_spacing):
            cv2.line(image, (0, y), (width, y), grid_color, line_thickness)

        # Draw vertical lines
        for x in range(0, width, grid_spacing):
            cv2.line(image, (x, 0), (x, height), grid_color, line_thickness)

    def display_image(self, image):
        #if len(image.shape) == 2:  # Color image (BGR)
        #    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Converting 12 bits (from camera) to 16 bits  for CV2:

        """ this adds a lot of overhead, so I changed to Mono8 in Detector line 74.

        image_16 = np.left_shift(image, 4)
        image_display = np.clip(image_16, 0, 65535)"""

        #self.add_grid(image) this is rendered very badly.

        height= image.shape[0]
        width = image.shape[1]
        bytes_per_line = width
        #bytes_per_line = 2* width <- this is for 16 bits greyscales
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        self.display_label.setPixmap(pixmap)
        self.display_label.setScaledContents(False)
        self.display_label.setPixmap(pixmap.scaled(self.display_label.size(),
                                                   aspectRatioMode=Qt.KeepAspectRatio))

    def show_warning(self, title, message):
        warning = myWarningBox(title=title, message=message, parent=self)
        warning.show_warning()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CamViewer()
    window.show()
    sys.exit(app.exec_())
