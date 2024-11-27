from ControlCenter.Laser import *
from ControlCenter.MotorControls import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from ControlCenter.Control_Utilities import Connection_initer
from ControlCenter.MeasurementControls import *
from PyQt5.QtWidgets import QApplication


class MainLTPApp:
    def __init__(self):

        self.PMAC_credentials = self.PMAC_connector()
        if not self.PMAC_credentials:
            self.show_warning("Connection issues", "Connection initialization Cancelled")
            return

        # first init motor controls to connect to Pmac, init motors, laser and Camera, loading also the graphics.
        self.motor_controls = MotorControls(self.PMAC_credentials)
        self.laser = LaserControl()
        # self.camera = Camera()
        self.controls = MeasurementControls(self.PMAC_credentials)

    def PMAC_connector(self):
        conn_initer = Connection_initer()
        credentials = conn_initer.get_credentials()
        if credentials is None:
            return None
        return credentials

    def run(self):
        self.laser.show()
        self.motor_controls.show()
        self.controls.show()

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