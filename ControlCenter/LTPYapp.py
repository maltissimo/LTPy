from ControlCenter.Laser import *
from ControlCenter.MotorControls import *
from ControlCenter.MeasurementControls import *
from PyQt5.QtWidgets import QApplication


class MainLTPApp:
    def __init__(self):
        # first init motor controls to connect to Pmac, init motors, laser and Camera, loading also the graphics.
        self.motor_controls = MotorControls()
        self.laser = Laser()
        # self.camera = Camera()
        self.controls = MeasurementControls()

    def run(self):
        self.laser.show()
        self.motor_controls.show()
        self.controls.show()

if __name__ == "__main__":
    app = QApplication([])
    main_app = MainLTPApp()
    main_app.run()
    app.exec_()  # Event loop for PyQt