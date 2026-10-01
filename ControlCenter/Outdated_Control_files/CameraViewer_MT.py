import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QTransform

from ControlCenter import MathUtils
from Graphics.Outdated_GUI_files.CameraViewer_GUI2 import Ui_PylonCamViewer
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from Hardware.Detector import Camera

class CamViewer(QMainWindow):
    def __init__(self, detector = None):
        super().__init__()
        self.gui = Ui_PylonCamViewer()
        self.gui.setupUi(self)

        # Button Connections
        self.gui.StartGrab.clicked.connect(self.start_grab)
        self.gui.StopGrab.clicked.connect(self.stop_grab)
        self.gui.SetAcqTime.clicked.connect(self.setAcqTime)

        if detector is not None:
            self.camera = detector
        else:
            self.camera = Camera()
        self.running = False

        # Fix 1: Use existing layout instead of creating a new one
        self.plot_layout = self.gui.CamFrame.layout()
        if self.plot_layout is None:
            self.plot_layout = QVBoxLayout(self.gui.CamFrame)
            self.plot_layout.setAlignment(Qt.AlignCenter)
        
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignCenter)
        # Fix 2: Ensure label expands to fill the frame so image is visible
        self.display_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_layout.addWidget(self.display_label)

        self.gui.StartGrab.setEnabled(True)
        self.gui.StopGrab.setEnabled(False)


        #Connecting the extra bits to the GUI:
        #self.gui.reset_frame_button.clicked.connect(self.camera.reset_sensor)
        #self.gui.height_lineedit.returnPressed.connect(self.set_acq_size)
        #self.gui.width_lineedit.returnPressed.connect(self.set_acq_size)
        #self.gui.acq_size_set.clicked.connect(self.set_acq_size)
        #self.gui.width_lineedit.setValidator(QIntValidator(48, 5280))
        #self.gui.height_lineedit.setValidator(QIntValidator(4, 4600))
        #frame_text = "4600x5280 px (W x H)"
        #self.gui.frame_size_label.setText(frame_text)

    """def set_acq_size(self):
        mewidth = None
        meheight = None

        # Check Width Input
        width_text = self.gui.width_lineedit.text()
        if width_text:
            try:
                mewidth = int(width_text)
                self.gui.width_lineedit.clear()
            except ValueError:
                pass

        # Check Height Input
        height_text = self.gui.height_lineedit.text()
        if height_text:
            try:
                meheight = int(height_text)
                self.gui.height_lineedit.clear()
            except ValueError:
                pass

        # Only call set_roi if at least one value is present
        if mewidth is not None or meheight is not None:
            self.camera.set_roi(width=mewidth, height=meheight)

            # Update label with current camera values
            # Note: Accessing GetValue() might be Pylon specific, using the wrapper methods is safer if available
            # or just reading back the properties we set if the camera object updates them.
            # Assuming self.camera.width and .height are updated in set_roi
            current_w = self.camera.width
            current_h = self.camera.height
            me_text = f"{current_h} x {current_w} H x W"
            self.gui.frame_size_label.setText(me_text)"""

    def start_grab(self):
        """self.timer.start(100)  # Update every 100 ms
        self.timer.timeout.connect(self.grab_data)"""
        if not self.running:
            self.running = True
            self.gui.StartGrab.setEnabled(False)
            self.gui.StopGrab.setEnabled(True)
            # self.camera.startgrabbing()
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

    def stop_while_measuring(self):
        self.running = False

    def grab_data(self):
        if self.running:
            self.camera.grabdata()
        if self.camera.frame is not None:
            #image = self.camera.frame

            if self.gui.FWHM_checkBox.isChecked():
                self.display_fwhm(self.camera.frame)

            if self.gui.centroid_checkBox.isChecked():
                self.display_centroid(self.camera.frame)

            self.plot_center_mark(self.camera.frame)
            self.display_image(self.camera.frame)

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
        fwhm_X, fwhm_Y = MathUtils.calc_2D_fwhm(nparray2D)
        fwhm_X = round((2.74 * fwhm_X), 2)
        fwhm_Y = round((2.74 * fwhm_Y), 2)

        # ==============================================================================
        # CONFIGURATION: CAMERA ROTATION (90 deg Clockwise)
        # ==============================================================================
        # Uncomment this block for 90-degree rotated camera (Vertical ROI)
        self.gui.FWHMX_label.setText(str(fwhm_Y))
        self.gui.FWHMY_label.setText(str(fwhm_X))
        # ==============================================================================

        # ==============================================================================
        # CONFIGURATION: STANDARD ORIENTATION (0 deg)
        # ==============================================================================
        # Uncomment this block for standard camera orientation (Horizontal ROI)
        # self.gui.FWHMX_label.setText(str(fwhm_X))
        # self.gui.FWHMY_label.setText(str(fwhm_Y))
        # ==============================================================================

    def display_centroid(self, nparray2D):
        centroid = MathUtils.centroid(nparray2D)
        centroidX = round(centroid[1], 0)
        centroidY = round(centroid[0], 0)

        # ==============================================================================
        # CONFIGURATION: CAMERA ROTATION (90 deg Clockwise)
        # ==============================================================================
        # Uncomment this block for 90-degree rotated camera (Vertical ROI)
        self.gui.centroidX_label.setText(str(centroidY))
        self.gui.centroidY_label.setText(str(centroidX))
        # ==============================================================================

        # ==============================================================================
        # CONFIGURATION: STANDARD ORIENTATION (0 deg)
        # ==============================================================================
        # Uncomment this block for standard camera orientation (Horizontal ROI)
        # self.gui.centroidX_label.setText(str(centroidX))
        # self.gui.centroidY_label.setText(str(centroidY))
        # ==============================================================================

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

        # ==============================================================================
        # CONFIGURATION: CAMERA ROTATION (90 deg Clockwise)
        # ==============================================================================
        # Uncomment this block for 90-degree rotated camera (Vertical ROI)
        pixmap = pixmap.transformed(QTransform().rotate(90))
        # ==============================================================================

        # ==============================================================================
        # CONFIGURATION: STANDARD ORIENTATION (0 deg)
        # ==============================================================================
        # Uncomment this block for standard camera orientation (Horizontal ROI)
        # pass # No rotation needed
        # ==============================================================================

        # Fix: Simplified display logic to ensure image is shown
        if not pixmap.isNull():
            self.display_label.setPixmap(pixmap.scaled(self.display_label.size(),
                                                       aspectRatioMode=Qt.KeepAspectRatio,
                                                       transformMode=Qt.SmoothTransformation))

    def show_warning(self, title, message):
        warning = myWarningBox(title=title, message=message, parent=self)
        warning.show_warning()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CamViewer()
    window.show()
    sys.exit(app.exec_())
