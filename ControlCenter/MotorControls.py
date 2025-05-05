from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMainWindow
import sys
import time
from Communication.MCG import *
from ControlCenter.Control_Utilities import Connection_initer as Conn_init
from ControlCenter.Control_Utilities import Utilities as Uti
from ControlCenter.Control_Utilities import CoordMessenger
from ControlCenter.MultiThreading import WorkerThread, SpeedWorker, synchronized_method, MoveWorker
from Graphics.Base_Classes_graphics.Motors_GUI import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from Hardware.Motors import MotorUtil, CompMotor


class MotorControls(QMainWindow):
    def __init__(self, shell : Gantry):

        super().__init__()

        # Create an instance of the Motors.GUI class:

        self.gui = Ui_Motors()
        self.gui.setupUi(self)

        self.motor1 = None
        self.motor2 = None
        self.motor3 = None
        self.X = None
        self.Y = None
        self.Z = None
        self.pitch = None
        self.roll = None
        self.yaw = None

        self.xmove = None
        self.ymove = None
        self.zmove = None
        self.yawmove = None
        self.pitchmove = None
        self.rollmove = None
        self.mot2move = None
        self.move_distance = None

        self.full_motorslist = []
        self.motorname_list = []
        self.movesdict = {}
        #print(type(self.movesdict))
        self.allMotors_inited = False
        self.allMoves_inited = False

        if shell is not None:
            self.shell = shell
        else:
            self.shell = Uti.connect2Pmac()

        print("Shell is live: ", self.shell.alive)
        #Multithreading facilities
        self.messenger = getattr(self, "messenger", None) or CoordMessenger(connection=self.shell, sleep_time=100)
        # Instantiating an object of MotorUtil class
        self.util = Uti.create(my_object="util", connection=self.shell)
        # Assigning motors and moves:
        self.init_motors()
        self.set_motorname_list()
        self.init_moves()
        self.update_dict()

        self.messenger.worker.update_signal.connect(self.update_all)

        #Connect the various bits in the UI:

        self.gui.pushButton_2.clicked.connect(self.movemotor)
        # This line here below connects to the PMAC.
        self.gui.connect.clicked.connect(Uti.connect2Pmac)


        try:
            self.gui.ResetAll.clicked.connect(MotorUtil.resetGantry)
            if not self.shell.alive:
                raise ConnectionError("No connection to PMAC")
            # QtWidgets.QMessageBox.warning("System reset!"   )
        except ConnectionError as e:
            QtWidgets.QMessageBox.warning(self, "Connection Error: ", str(e))

        try:
            self.gui.HomeGantry.clicked.connect(MotorUtil.homeGantry)
            if not self.shell.alive:
                raise ConnectionResetError("No connection to PMAC")
            self.gui.sh_display.turn_green()
            # QtWidgets.QMessageBox.warning("System homed!")
        except ConnectionError as e:
            QtWidgets.QMessageBox.warning(self, "Connection Error", str(e))

        self.gui.pushButton.clicked.connect(self.stopall)
        self.gui.setspeed.clicked.connect(self.set_speed)

        self.gui.getspeed.clicked.connect(self.get_speed)

        # Filling the data for comboboxes:

        self.gui.motor_selector.addItems(self.movesdict.keys())
        self.gui.motor_selector_2.addItems(self.motorname_list)

        # Comboboxes behavior

        self.gui.motor_selector.currentIndexChanged.connect(self.update_units)
        self.gui.motor_selector_2.currentIndexChanged.connect(self.update_units)
        # Used twice, so that if a user changes in one tab, the other is automatically changed by the update_units method

        self.gui.units.setText("µm")

        self.gui.distance.enter_pressed.connect(self.update_distance)

        # Warning for RTT stage parallelism angles
        parallel = myWarningBox(title = "Attention!",
                                message = " RTT flat @ Pitch = -0.05 and Roll = -0.01 deg!")
        parallel.show_warning()

        self.start_coord_monitoring()
        self.update_all()

    def init_motors(self):
        print("Initing Motor objects, standby...")
        mylist = self.util.motors()
        #print("List of motors on the system: :", mylist)

        try:
            self.motor1 = Uti.motors_init(connection = self.shell, motorID = mylist[0][1], cs= mylist[0][0])
            self.motor2 = Uti.motors_init(connection=self.shell, motorID = mylist[1][1], cs = mylist[1][0])
            self.motor3 = Uti.motors_init(connection=self.shell, motorID = mylist[2][1], cs = mylist[2][0])

            self.yaw = Uti.motors_init(connection= self.shell, motorID = mylist[3][1], cs = mylist[3][0])
            self.X = Uti.motors_init(connection= self.shell, motorID = mylist[4][1], cs=  mylist[4][0])
            self.Y = Uti.motors_init(connection= self.shell, motorID = mylist[5][1], cs = mylist[5][0])

            self.Z = Uti.motors_init(connection = self.shell, pmac_name = "Z", cs = 1)
            self.pitch = Uti.motors_init(connection = self.shell, pmac_name = "B", cs = 1)
            self.roll = Uti.motors_init(connection = self.shell, pmac_name = "A", cs = 1)


            if self.shell is None or self.shell.alive == False or self.shell.isinit == False:

                raise ValueError ("Trying to init motor, but Pmac not connected or not correctly inited!")

            self.allMotors_inited = True
            self.full_motorslist = [
                self.motor1,
                self.motor2,
                self.motor3,
                self.yaw,
                self.X,
                self.Y,
                self.Z,
                self.pitch,
                self.roll
            ]

            self.user_motorlist = [
                self.X,
                self.Y,
                self.Z,
                self.pitch,
                self.roll,
                self.yaw
            ]

            #QtWidgets.QMessageBox.warning(self, "All motors correctly initialized!")

            #Filling the data for comboboxes:

            """for motor in self.user_motorlist:
                self.gui.motor_selector_2.addItem((str(motor)))
                self.gui.motor_selector.addItem(str(motor))"""

            self.allMotors_inited = True
            print("Motor objects succsesfully inited.")

        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "ERROR!", str(e))

    def init_moves(self):
        print("initing move objects, standby...")
        """ debugging lines: 
        
            for motor in self.user_motorlist:
            print(type(motor))
            if hasattr(motor, "motorID"):
                print("Motor ID and type MotorID: ", motor.motorID, type(motor.motorID))

            print("Motor's pmac name: ", motor.pmac_name)"""
        try:
            self.xmove = Uti.init_moves(connection = self.shell, motor = self.X, util = self.util)
            self.ymove = Uti.init_moves(connection=self.shell,  motor = self.Y, util = self.util)
            self.zmove = Uti.init_moves(connection = self.shell, motor = self.Z, util = self.util)
            self.pitchmove = Uti.init_moves(connection = self.shell, motor = self.pitch, util = self.util)
            self.rollmove = Uti.init_moves(connection = self.shell, motor = self.roll, util = self.util)
            self.yawmove = Uti.init_moves(connection = self.shell, motor = self.yaw, util = self.util)

            if self.shell is None or self.shell.alive == False or self.shell.isinit == False:
                raise ValueError("Trying to init moves, but Pmac not connected or not correctly inited!")
            self.allMoves_inited = True
            print("Move objects successfully inited.")
        except ValueError as e:
            QtWidgets.QMessageBox(self, "Error!", str(e))

        print( "At the end of the rainbow, moves correctly initialized!")

    def update_dict(self):
        self.movesdict = {"X": self.xmove,
                          "Y": self.ymove,
                          "Z": self.zmove,
                          "pitch": self.pitchmove,
                          "roll": self.rollmove,
                          "yaw": self.yawmove
                          }

    def update_units(self):
        """
        this methods is used to change the labels displaying the units of measurement in the Motors and the Utilities tab
        :return:
        """
        index = self.gui.motor_selector.currentIndex()
        if index <= 2:
            self.gui.units.setText("µm") # units is the name of the label in  the Motors tab
            self.gui.label.setText("µm") # label is the name of the label in the Utilities tab
        elif index > 2:
            self.gui.label.setText("degrees") # label is the name of the label in the Utilities tab
            self.gui.units.setText("degrees") # units is the name of the label in  the Motors tab

    def set_motorname_list(self):
        self.motorname_list = [
            self.X.motorname,
            self.Y.motorname,
            self.Z.pmac_name,
            "pitch",
            "roll",
            "yaw"
        ]

    def update_distance (self):
        index = self.gui.motor_selector_2.currentIndex
        if index <= 2:
            self.gui.label.setText("µm")
        elif index >2:
           self.gui.label.setText ("degrees")

    def start_coord_monitoring(self):
        if not self.messenger.worker.isRunning():
            print("starting worker thread")
            self.messenger.start()
        else:
            print("Worker already working")

    def stop_coord_monitoring(self):
        self.messenger.stop()

    def get_all_pos(self):
        return self.messenger.coordinates

    def update_all(self):
        """02 December 2024: This will now change, as there is a quicker way to update motor:
        &1,2,3p
        this will report on ACTUAL position, which is what is needed.The request is now per
        the output is stored in shell.textoutput, as an array:
        By setting:
        alan = shell.textoutput
        alan can then be called, very convieniently!!, as
        alan[n] reporting all the actual positions of motors in CSn
        Splitting then allows for actual number reading.

        """
        #print("[update_all] called")
        i = 0
        #print(self.messenger.coordinates)
        for self.motor in self.user_motorlist:
            name = str(self.motorname_list[i])
            #print("name is : ", name)
            display = name.lower() + "_display"
            line_edit = getattr(self.gui, display, None)
            if line_edit:
                #print(f"Found line_edit for {display}")
                #print(self.messenger.coordinates[name])
                number = round(float(self.messenger.coordinates.get(name)), 3)
                formatted_number = f"{number:.6e}"
                line_edit.setText(str(formatted_number))
            else:
                print(display, " not found in the class or its parents")
            i = i + 1

        if not self.shell.alive:
            self.gui.pmac_display.turn_red()
        elif self.shell.alive:
            self.gui.pmac_display.turn_green()

    def on_get_speed_clicked(self):
        worker = SpeedWorker(self.get_speed)
        QThreadPool.globalInstance().start(worker)

    def cleanup_worker(self):
        self.worker = None

    def get_speed(self):
        self.messenger.pause()# Pause updates while fetching speed
        index = self.gui.motor_selector_2.currentIndex()
        self.motor = self.user_motorlist[index]
        #print("request for: ", self.motor.pmac_name)

        #print(f"Getting speed for motor: {self.motor}")  # Debugging print

        try:
            act_speed = self.motor.getjogspeed()
            #print(f"Retrieved speed: {act_speed}")  # Debugging print
            #act_speed = round(act_speed, 2)
            self.gui.set_display.setText(str(act_speed))
        except Exception as e:
            print(f"Error retrieving speed: {e}")  # Catch and print any error
            QtWidgets.QMessageBox.warning(self, "Error!", f"Failed to get speed: {str(e)}")
        finally:
           self.messenger.resume()

    def on_set_speed_clicked(self):
        worker = SpeedWorker(self.set_speed)
        QThreadPool.globalInstance().start(worker)
    def set_speed(self):
        self.messenger.pause()
        index = self.gui.motor_selector_2.currentIndex()
        # Motors in motor_selector_2 are from user_motorlist, so:
        self.motor= self.user_motorlist[index]

        #motor = self.gui.motor_selector_2.itemText(index)

        speed = self.gui.set_display.text()
        #print(speed, type(speed))

        self.motor.setjogspeed(float(speed))
        self.messenger.resume()
        #self.get_speed() # this is just a sanity check...

    def stopall(self):
        message = "#*kill"
        self.shell.send_message(message)
        killed = myWarningBox(title = "Warning!!", message = "All motors killed, /n the Gantry needs a reset & home!")
        killed.show_warning()
    def movemotor(self):
        motorkey = self.gui.motor_selector.currentText()
        # print(type(self.movesdict))
        self.mot2move = self.movesdict.get(motorkey) # This should be a Move object, i.e. xmove, ymove, ..., yawmove
        self.move_distance = float(self.gui.distance.on_enter_pressed())
        self.move_worker = MoveWorker(self.mot2move)

        self.move_worker.begin_signal.connect(self.on_move_begin)
        self.move_worker.end_signal.connect(self.on_move_end)
        self.move_worker.update_signal.connect(self.still_moving)
        self.move_worker.start()

    @synchronized_method
    def on_move_begin(self):

        if not self.gui.move_rel.isChecked() and not self.gui.move_abs.isChecked():
            try:
                raise ValueError("Check either Move Rel or Move Abs")
            except ValueError as e:
                QtWidgets.QMessageBox.warning(self, "Error!", str(e))

        #Move Relative:
        elif self.gui.move_rel.isChecked() and not self.gui.move_abs.isChecked():
            self.gui.pushButton_2.setEnabled(False)
            self.messenger.pause()
            self.mot2move.move_rel(distance = self.move_distance )


        #Move Absolute:
        elif not self.gui.move_rel.isChecked() and self.gui.move_abs.isChecked():
            self.gui.pushButton_2.setEnabled(False)
            self.messenger.pause()
            self.mot2move.move_abs(coord = self.move_distance)

    #@synchronized_method
    def on_move_end(self):
        #print("[Controller] on_move_end triggered")
        self.gui.pushButton_2.setEnabled(True)
        self.mot2move.movecomplete = True

        self.messenger.resume()
        self.mot2move = None
        self.move_distance = None

    def still_moving(self, in_pos):
        if self.mot2move is not None:
            if in_pos == 1:
                return


    def pause_timer(self):
        self.timer.stop()

    def restartTimer(self):
        self.timer.start()

    def resetGantry (self):
        MotorUtil.resetGantry()
        reset = myWarningBox(title = "Warning!", message = "Gantry reset, press the Home button!")
        reset.show_warning()

    def homeGantry(self):
        MotorUtil.resetGantry()
        while not self.MotorUtil.gantryHomed():
            time.sleep(2)
        homed = myWarningBox(title="Success!", message="Home Completed")
        homed.show_warning()

    def closeEvent(self, event):
        """Handle cleanup before closing the window."""
        reply = QMessageBox.question(
            self, "Exit Confirmation", "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.stop_coord_monitoring()  # Stop monitoring
            self.shell.close_connection()  # Close SSH connection if applicable
            event.accept()  # Allow the window to close
        else:
            event.ignore()  # Prevent the window from closing


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MotorControls(None)#20241127 MA: Added None as the class requires the PMAC credentials as parameter.
    window.show()
    app.exec_()
