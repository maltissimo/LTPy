import sys
from PyQt5 import QtWidgets
from Graphics.Base_Classes_graphics.LaserGUI2 import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from ControlCenter.Control_Utilities import Utilities as Uti
from PyQt5.QtCore import QTimer
from Hardware.Source import *
from ControlCenter.MultiThreading import *

def synchronized_method(method):
    outer_lock = threading.Lock()
    lock_name = "__" + method.__name__ + "__lock" + "__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name):
                setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

    return sync_method

class LaserControl(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        #Create an instance of the Laser_GUI class:
        self.gui = Ui_LaserController()
        self.gui.setupUi(self)

        #Creating an instance of the laser class:
        self.source = Uti.create(my_object= "laser")
        self.laserON = self.source.is_on

        #Worker thread:
        self.worker_thread = WorkerThread(self.update_all)

        self.worker_thread.update_signal.connect(self.handle_update)
        self.worker_thread.begin_signal.connect(self.handle_start)
        self.worker_thread.end_signal.connect(self.handle_end)
        #self.worker_thread.error_signal.connect(self.handle_error)

        """self.timer = QTimer()
        self.timer.start(100)  #Updating every 100 ms.
        self.timer.timeout.connect(self.update_all) # connects to the update_all method
        """
        #Connect the various bits in the UI:

        self.gui.pushButton.clicked.connect(self.toggle_laser)

        self.gui.horizontalSlider.setMinimum(0)
        self.gui.horizontalSlider.setMaximum(1000)
        self.gui.horizontalSlider.setValue(0)
        self.gui.horizontalSlider.valueChanged.connect(self.slider_change)

    def handle_start(self):
        return

    def handle_end(self):
        return

    def showEvent(self, event):
        """
        starts he worker thread when the window is shown
        """

        super().showEvent(event)
        self.worker_thread.start()

    def closeEvent(self, event):
        """
        Stops the worker thread when the window is closed.
        """
        self.worker_thread.stop()
        super().closeEvent(event)

    def update_comms_label(self, status):
        if status =="ON":
            self.gui.comms_onoff.setText("ON")
            self.gui.comms_onoff.turn_green()
        elif status == "OFF":
            self.gui.comms_onoff.setText("OFF")
            self.gui.comms_onoff.turn_red()

    def update_laser_label(self, status):
        if status == "ON":
            self.gui.laser_onoff.setText("ON")
            self.gui.laser_onoff.turn_green()
            self.laserON = True
        elif status == "OFF":
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
            self.source.set_power(pow) # sets the POWer Level preset to 10% of max power
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
        try:
            current = self.source.serialmessage(isOUTCURLEVEL)
            power_preset = self.source.serialmessage(isLASPOWLEVEL)
            power = self.source.serialmessage(isOUTPOWLEVEL)
            slider_value = self.slider_value(power_preset)

            # Verify numerical values before updating
            if not current.replace('.', '', 1).isdigit():
                print(f"Invalid current value: {current}")
                current = "0.0"

            if not power.replace('.', '', 1).isdigit():
                print(f"Invalid power value: {power}")
                power = "0.0"

            data = {
                "current": current,
                "power_preset": power_preset,
                "power": power,
                "wavelength": self.source.wlength,
                "slider_value": slider_value,
                "comms_status": self.source.serialmessage(isHSHAKE),
                "laser_status": self.source.is_on
            }

            self.worker_thread.update_signal.emit(data)
        except Exception as e:
            print(f"Error in update_all: {e}")

    def handle_update(self, data):
        #print(f"Update data: {data}") # Log data for debugging
        self.update_comms_label(data["comms_status"])
        self.update_laser_label(data["laser_status"])
        self.gui.cur_display.updateValue(data["current"])
        self.gui.int_display.updateValue(data["power"])
        self.gui.wlength_display.updateValue(data["wavelength"])
        self.gui.horizontalSlider.setValue(data["slider_value"])


    def handle_error(self, error_message):
        mymessage = f"Error in worker thread: {error_message}"
        self.show_warning(title = "Warning!", message = mymessage)

    def show_warning(self, title, message):
        warning = myWarningBox(
            title=title,
            message=message,
            parent=self
        )
        warning.show_warning()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LaserControl()
    window.show()
    sys.exit(app.exec_())

