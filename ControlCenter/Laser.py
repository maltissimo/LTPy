import sys
from PyQt5 import QtWidgets
from Graphics.Base_Classes_graphics.LaserGUI2 import *
from ControlCenter.Control_Utilities import Utilities as Uti
from PyQt5.QtCore import QTimer
from Hardware.Source import *


class __LaserControl(QtWidgets.QMainWindow):

    def __init__(self): """, laser_timer: QTimer"""
        super().__init__()

        #Create an instance of the Laser_GUI class:
        self.gui = Ui_LaserController()
        self.gui.setupUi(self)

        #Creating an instance of the laser class:
        self.source = Uti.create(my_object= "laser")
        self.laserON = self.source.is_on

        self.timer = laser_timer
        #self.timer.start(100)  #Updating every 100 ms.
        self.timer.timeout.connect(self.update_all) # connects to the update_all method

        #Connect the various bits in the UI:
        self.gui.pushButton.clicked.connect(self.toggle_laser)

        self.gui.horizontalSlider.setMinimum(0)
        self.gui.horizontalSlider.setMaximum(1000)
        self.gui.horizontalSlider.setValue(0)
        self.gui.horizontalSlider.valueChanged.connect(self.slider_change)


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
            self.gui.int_display.updateValue("0.000")
        elif self.source.is_on == "OFF":
            pow = 0.1 * float(self.source.p_high_lim)
            self.source.set_power(pow) # sets the POWer Level preset to 80% of max power
            self.source.turnON(LASON)
            self.source.is_on = "ON"

    def int_low_high(self):
        low = float(self.source.p_low_lim)
        high = float(self.source.p_high_lim)
        return ([low, high])

    def get_actual_int(self):

        return (self.source.pow_level)

    def getwlength(self):

        return (self.source.wlength)

    def curlevel(self):
        return (self.source.cur_level)

    def slider_value(self, act_value):
        """
        position is integers. So I'll divide the length in thousandths.
        the actual value is act, x is the value in thousandths, and high_lim is the top value:
        x = 1000 * act / highlim
        :return:
        """
        return int(1000 * float(act_value)/float(self.source.p_high_lim))

    def slider_change(self):

        slider_pos = self.gui.horizontalSlider.value()
        act_power = slider_pos * float(self.source.p_high_lim) / 1000
        self.source.set_power(act_power)

    def update_all(self):
        current = self.source.serialmessage(isOUTCURLEVEL)
        power_preset = self.source.serialmessage(isLASPOWLEVEL)
        power = self.source.serialmessage(isOUTPOWLEVEL)
        self.gui.cur_display.updateValue(current)  # updating laser current
        self.gui.int_display.updateValue(power)  # updating laser intensity
        self.gui.wlength_display.updateValue(self.getwlength())  # updating wavelength
        self.gui.horizontalSlider.setValue(self.slider_value(power_preset))
        self.update_comms_label()  # updating comms label
        self.update_laser_label()  # updating laser label


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LaserControl()
    window.show()
    sys.exit(app.exec_())

    #TODO:
    # Add a FWHM tool in the CamViewer option, for lens focus finding purposes
