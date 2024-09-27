import sys
from PyQt5 import QtWidgets
from Graphics.Base_Classes_graphics.Laser_GUI import *
from ControlCenter.Control_Utilities import Utilities as Uti
from PyQt5.QtCore import QTimer
from Hardware.Source import *


class LaserControl(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        #Create an instance of the Laser_GUI class:
        self.gui = Ui_LaserController()
        self.gui.setupUi(self)

        #Creating an instance of the laser class:
        self.source = Uti.create(my_object= "laser")
        self.laserON = self.source.is_on

        self.timer = QTimer(self)
        self.timer.start(200)  #Updating every 200 ms.
        self.timer.timeout.connect(self.update_all) # connects to the update_all method

        #Connect the various bits in the UI:
        self.gui.pushButton.clicked.connect(self.toggle_laser)
        self.gui.horizontalSlider.valueChanged.connect(self.source.set_power)

    def update_comms_label(self):
        if self.source.serialmessage(isHSHAKE) =="ON":
            self.gui.comms_onoff.setText("ON")
            self.gui.comms_onoff.turn_green()
        elif self.source.serialmessage(isHSHAKE) == "OFF":
            self.gui.comms_onoff.setText("OFF")
            self.gui.comms_onoff.turn_red()

    def update_laser_label(self):
        if self.source.is_on == "ON":
            self.gui.laser_onoff.setText("ON")
            self.gui.laser_onoff.turn_green()
            self.laserON = True
        elif self.source.is_on == "OFF":
            self.gui.laser_onoff.setText("OFF")
            self.gui.laser_onoff.turn_red()
            self.laserON = False

    def toggle_laser(self):
        if self.source.is_on == "ON":
            self.source.turnOFF(LASON)
            self.source.is_on = "OFF"
        elif self.source.is_on == "OFF":
            self.source.turnON(LASON)
            self.source.is_on = "ON"

    def int_low_high(self):
        low = self.source.p_low_lim
        high = self.source.p_high_lim
        return ([low, high])

    def get_actual_int(self):

        return (self.source.pow_level)

    def getwlength(self):

        return (self.source.wlength)

    def curlevel(self):
        return (self.source.cur_level)

    def update_all(self):
        self.gui.cur_display.updateValue(self.curlevel())  # updating laser current
        self.gui.int_display.updateValue(self.get_actual_int())  # updating laser intensity
        self.gui.wlength_display.updateValue(self.getwlength())  # updating wavelength
        self.update_comms_label()  # updating comms label
        self.update_laser_label()  # updating laser label

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LaserControl()
    window.show()
    sys.exit(app.exec_())

    #TODO: check why text is flickering inside the Laser window
    # check Laser intensity level working on slider.