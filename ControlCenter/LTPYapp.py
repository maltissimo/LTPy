from ControlCenter.Laser import *
from ControlCenter.MotorControls import *


class MainLTPApp:
    def __init__(self):
        # first init motor controls to connect to Pmac, init motors, laser and Camera, loading also the graphics.
        self.motor_controls = MotorControls()
        self.laser = Laser()
        self.camera = Camera()
        self.controls = MeasurementControls()

    def run(self):
        self.controls.show()
        self.motor_controls.show()
        self.laser.show()
