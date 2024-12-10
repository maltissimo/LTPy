from ControlCenter.Laser_MT import *
from ControlCenter.MotorControls_MT import *
from Graphics.Base_Classes_graphics.BaseClasses import *
from ControlCenter.Control_Utilities import Connection_initer
from ControlCenter.MeasurementControls_MT import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

class MainLTPApp:
    def __init__(self):

        self.PMAC_credentials = self.PMAC_connector()
        print(self.PMAC_credentials["ip"])
        print(self.PMAC_credentials["username"])
        print(self.PMAC_credentials["password"])

        if not self.PMAC_credentials:
            self.show_warning("Connection issues", "Connection initialization Cancelled")
            return

        # first init motor controls to connect to Pmac, init motors, laser and Camera, loading also the graphics.
        """
        Commented out as multi-threading is implemented in -Controls classes. 
        
        self.motor_timer = QTimer()
        self.motor_timer.setInterval(100)
        self.camera_timer = QTimer()
        self.camera_timer.setInterval(100)
        self.laser_timer = QTimer()
        self.laser_timer.setInterval(200)

        self.startAllTimers()"""

        self.motor_controls = MotorControls(self.PMAC_credentials)
        self.laser = LaserControl()
        # self.camera = Camera()
        self.controls = MeasurementControls(self.PMAC_credentials)

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
