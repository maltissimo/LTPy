import sys
from PyQt5 import QtWidgets
from Graphics.Base_Classes_graphics.LaserGUI2 import *
from ControlCenter.Control_Utilities import Utilities as Uti
from PyQt5.QtCore import QTimer
from Hardware.Source import *
from ControlCenter.MultiThreading import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox

class LaserControl(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        #Create an instance of the Laser_GUI class:
        self.gui = Ui_LaserController()
        self.gui.setupUi(self)

        #Creating an instance of the laser class:
        self.source = Uti.create(my_object= "laser")
        self.laserON = self.source.is_on
        self.warning = myWarningBox()


        """self.timer = QTimer()
        self.timer.start(100)  #Updating every 100 ms.
        self.timer.timeout.connect(self.update_all) # connects to the update_all method""" # Commented out MA 20250220

        #Connect the various bits in the UI:
        self.gui.pushButton.clicked.connect(self.toggle_laser)

        self.gui.horizontalSlider.setMinimum(0)
        self.gui.horizontalSlider.setMaximum(1000)
        self.gui.horizontalSlider.setValue(0)
        self.gui.horizontalSlider.valueChanged.connect(self.slider_change)

        self.show()

        # Create worker thread, calling self.source.get_all_status() every 100 ms.
        self.monitor_thread = WorkerThread(task=self.source.get_all_status, sleep_time=150)
        self.monitor_thread.update_signal.connect(self.update_gui)
        self.monitor_thread.error_signal.connect(lambda e: (self.warning.setText(e), self.warning.show_warning()))
        self.monitor_thread.begin_signal.connect(lambda: print("Monitoring started"))
        self.monitor_thread.end_signal.connect(lambda: print("Monitoring Stopped"))
        self.monitor_thread.start()

    def update_gui(self, status):
        """
        slots that receives the status dictionary emitted by the worker thread
        :param status: a dictionary from source.get_all_status()
        :return:
        """
        if "error" in status:
            self.warning.setText(status['error'])
            self.warning.show_warning()
            return

        self.gui.cur_display.updateValue(status.get("current", "N/A"))
        self.gui.int_display.updateValue(status.get("power", "N/A"))
        self.gui.wlength_display.updateValue(status.get("wlength", "N/A"))
        #Update slider based on power preset value.
        power_preset = status.get("power_preset", 0)
        self.gui.horizontalSlider.setValue((self.slider_value(power_preset)))
        #Update comms_label:
        comms = status.get("comms", "OFF")
        if comms =="ON":
            self.gui.comms_onoff.setText("ON")
            self.gui.comms_onoff.turn_green()
        else:
            self.gui.comms_onoff.setText("OFF")
            self.gui.comms_onoff.turn_red()
        #Update laser on/off label:
        if status.get("is_on", "OFF") == "ON":
            self.gui.laser_onoff.setText("ON")
            self.gui.laser_onoff.turn_green()
            self.laserON = True
        else:
            self.gui.laser_onoff.setText("OFF")
            self.gui.laser_onoff.turn_red()
            self.laserON = False

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
            pow = 0.5 * float(self.source.p_high_lim)
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
