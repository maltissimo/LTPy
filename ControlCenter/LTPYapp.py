
from ControlCenter.Laser_MT import LaserControl
from ControlCenter.MotorControls_MT import *
from Graphics.Base_Classes_graphics.BaseClasses import *
from ControlCenter.Control_Utilities import Connection_initer
from ControlCenter.MeasurementControls import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from Graphics.MainLTPyApp_GUI import *

from Graphics.CameraViewer_MT import CamViewer


class MainLTPApp:
    def __init__(self):
        self.PMAC_credentials = []

        #Check connection to PMAC, and ask user if not connected.

        self.check_PMAC_connection()

        #first init the GUI:
        self.gui = LTPy_MainWindow()
        self.gui.setupUI()

        self.laser = None
        self.cam = None
        self.motor_controls = None
        self.controls = None

        #Connecting clicks to methods:

        self.gui.LaserButton.clicked.connect(self.startLaserControls)
        self.gui.MeasurementButton.clicked.connect(self.startMeasurementControls)
        self.gui.MotorsButton.clicked.connect(self.startMotorControls)
        self.gui.CamButton.clicked.connect(self.startCameraControls)
        self.gui.QuitButton.clicked.connect(self.exitLTPy)

    def exitLTPy(self):
        pass
    def startLaserControls(self):
        self.laser = Laser()
        self.laser.show()

    def startMeasurementControls(self):

        if self.PMAC_credentials is not None:
            self.controls = MeasurementControls(self.PMAC_credentials)
        else:
            self.PMAC_credentials = self.PMAC_connector()
            self.controls = MeasurementControls(self.PMAC_credentials)
        self.controls.show()

    def startMotorsControls(self):

        if self.PMAC_credentials is not None:
            self.motor_controls = MotorControls(self.PMAC_credentials)
        else:
            self.PMAC_credentials = self.PMAC_connector()
            self.motor_controls = MeasurementControls(self.PMAC_credentials)
        self.motor_controls.show()

    def startCameraControls(self):
        if self.controls is None:
            self.cam = CamViewer()
            self.cam.show()

        else:
            self.show_warning(title= "Warning!", message = "Camera already in use")








        self.PMAC_credentials = self.PMAC_connector()
        if not self.PMAC_credentials:
            self.show_warning("Connection issues", "Connection initialization Cancelled")
            return

        # first init motor controls to connect to Pmac, init motors, laser and Camera, loading also the graphics.


        self.startAllTimers()

        self.motor_controls = MotorControls(self.PMAC_credentials, self.motor_timer)
        self.laser = LaserControl(self.laser_timer)
        # self.camera = Camera()
        self.controls = MeasurementControls(self.PMAC_credentials, self.motor_timer, self.camera_timer)

    def check_PMAC_connection(self):
        if self.PMAC_credentials:
            return
        else:
            self.PMAC_credentials = self.PMAC_connector()
        if not self.PMAC_credentials:
            self.show_warning("Connection issues", "Connection initialization Cancelled")
            return

    def startAllTimers(self):
        for element in self.__dict__.values():
            if isinstance(element, QTimer):
                element.start()

    def stopAllTimers(self):
        for element in self.__dict__.values():
            if isinstance(element, QTimer):
                element.stop()

    def stopTimer(self, QTimerObject):
        QTimerObject.stop()

    def PMAC_connector(self):
        conn_initer = Connection_initer()
        credentials = conn_initer.get_credentials()
        if credentials is None:
            return None
        return credentials

    def show_warning(self, title, message):
        warning = myWarningBox(
            title=title,
            message=message,
            parent=self
        )
        warning.show_warning()

if __name__ == "__main__":
    app = QApplication([])
    main_app = MainLTPApp()
    main_app.run()
    app.exec_()  # Event loop for PyQt