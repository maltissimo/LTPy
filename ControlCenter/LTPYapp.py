from ControlCenter.Laser import LaserControl
from ControlCenter.MotorControls import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from ControlCenter.Control_Utilities import Connection_initer, SSHConnectionManager
from ControlCenter.MeasurementControls import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

class MainLTPApp:
    def __init__(self):
        self.PMAC_credentials = None

        self.PMAC_credentials = self.PMAC_connector()
        """print(self.PMAC_credentials["ip"])
        print(self.PMAC_credentials["username"])
        print(self.PMAC_credentials["password"])"""

        if not self.PMAC_credentials:
            cred_warning = myWarningBox("Connection issues", "Connection initialization Cancelled")
            cred_warning.show_warning()
            return

        print(self.PMAC_credentials)

        try:
            self.manager = SSHConnectionManager.get_instance(self.PMAC_credentials)
        except Exception as e:
            conn_warning = myWarningBox(title = "Conn error", message = str({e}))
            conn_warning.show_warning()
            return
        shared_connection = self.manager.get_connection()

        self.motor_controls = MotorControls(shared_connection)
        self.laser = LaserControl()
        self.controls = MeasurementControls(shell = shared_connection,
                                            motors = self.motor_controls)

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



if __name__ == "__main__":
    app = QApplication([])
    main_app = MainLTPApp()
    main_app.run()
    app.exec_()  # Event loop for PyQt
