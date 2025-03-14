from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow
import sys

from ControlCenter.Control_Utilities import Connection_initer as Conn_init
from ControlCenter.Control_Utilities import Utilities as Uti
from Graphics.Base_Classes_graphics.Motors_GUI import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from Hardware.Motors import MotorUtil, CompMotor


class MotorControls(QMainWindow):
    def __init__(self, PMAC_credentials):
        if not PMAC_credentials:
            connector = Conn_init()
            PMAC_credentials = connector.get_credentials()

        print("inside MotorControls: ")
        print(PMAC_credentials["ip"])
        print(PMAC_credentials["username"])
        print(PMAC_credentials["password"])

        self.pmac_ip = PMAC_credentials["ip"]
        #print(self.pmac_ip)
        self.pmac_username = PMAC_credentials["username"]
        #print(self.pmac_username)
        self.pmac_password = PMAC_credentials["password"]
        #print(self.pmac_password)

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

        self.full_motorslist = []
        self.motorname_list = []
        self.movesdict = {}
        #print(type(self.movesdict))
        self.allMotors_inited = False
        self.allMoves_inited = False

        self.username = None
        if self.pmac_ip is None:
            self.pmac_ip = "127.0.0.200" # adding a default for safety.
        self.password = None
        self.shell = Uti.create(my_object = "shell") # Instantiating an object of Shell class
        print("Shell is live: ", self.shell.alive)

        if self.shell.alive == False :

            self.shell.pmac_ip = self.pmac_ip
            #print("Shell ip: ", self.shell.pmac_ip)
            self.shell.username = self.pmac_username
            #print("Shell username: ", self.shell.username)
            self.shell.password =  self.pmac_password
            #print("Sell pwd: ", self.shell.password)

            # Initing shell and PMAC

            print("Now connecting to PMAC...")

            self.shell.openssh() # opening the channel to PMAC
            print("Connected!")
            print("Initing the PMAC input... ")
            self.shell.pmac_init() # initing the PMAC
            if not self.shell.isinit:
                self.shell.pmac_init()

            self.shell.set_echo()

            # Finished setting the PMAC.
            print(self.shell.status())
            print("Done!")


        self.util = Uti.create(my_object="util", connection = self.shell)  # Instantiating an object of MotorUtil class
                                                        # self.shell and self.util have to be inited correctly.
        # Assigning motors and moves:

        self.init_motors()
        self.set_motorname_list()
        self.init_moves()

        # since moves are all inited, calling the update_dict() method will simply update the self.movesict attribute:

        self.update_dict()
        #print(self.movesdict) this is for debugging

        #Connect the various bits in the UI:

        self.gui.pushButton_2.clicked.connect(self.movemotor)
        # This line here below connects to the PMAC.
        self.gui.connect.clicked.connect(self.Connect2_Pmac)

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
        self.timer = QTimer()

        self.timer.start(100)   #updating every 100 ms
        self.timer.timeout.connect(self.update_all)  # connects to the update_all method

        # Warning for RTT stage parallelism angles
        parallel = myWarningBox(title = "Attention!", message = " RTT flat @ Pitch = -0.01 and Roll = -0.01 deg!")
        parallel.show_warning()

    def Connect2_Pmac(self):
        """
        This method connects to the PMAC with the proper values of IP, Username and passwords
        :return:
        """

        try:

            self.shell.username = self.username
            self.shell.password = self.password
            self.shell.pmac_ip = self.pmac_ip
            if self.shell.username or self.shell.password or self.shell.pmac_ip is None:
                raise ValueError("Please input all the values")
            # this happens if username, pmac_ip and password are correct:

            self.shell.openssh()
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Input Error ", str(e))

        #turning the lights green
        if self.shell.alive:
            self.gui.pmac_display.turn_green()
        try:

            self.shell.pmac_init()
            if not self.shell.isinit:
                raise ValueError ("Error initializing the PMAC!")
            self.shell.set_echo()
            QtWidgets.QMessageBox.warning(self, "PMAC correctly initialized!")

        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "ERROR!", str(e))

    def init_motors(self):
        print("Initing Motor objects, standby...")
        mylist = self.util.motors()

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

    def update_all_positions(self):
        """02 December 2024: This will now change, as there is a quicker way to update motor:
        &1,2,3p
        this will report on ACTUAL position, which is what is needed.
        the output is stored in shell.textoutput, as an array:
        By setting:
        alan = shell.textoutput
        alan can then be called, very convieniently!!, as
        alan[n] reporting all the actual positions of motors in CSn
        Splitting then allows for actual number reading.

        """

        self.shell.send_receive("&1,2,3p")
        all_pos_array = self.shell.textoutput
        CS1 = all_pos_array[1].split() # this is for A, B and Z, i.e. roll, pitch and Z
        CS2 = all_pos_array[2].split() # this is for C, i.e. yaw
        CS3 = all_pos_array[3].split() # this is for X and Y.
        try:
            self.pitch.real_pos = float(CS1[1][1:]) # this is B i.e. pitch
            self.roll.real_pos = float(CS1 [0][1:]) # this is A, i.e. roll
            self.Z.real_pos = float(CS1 [2][1:])
            self.yaw.real_pos = float(CS2[0][1:])
            self.X.real_pos = float(CS3[0][1:])
            self.Y.real_pos = float(CS3[1][1:])
        except ValueError:
            print("MotorName not initialized correctly!! ")
        i = 0

        for self.motor in self.user_motorlist:
            #print(self.motor.pmac_name)
            #self.motor.real_pos = self.motor.get_real_pos()
            #print(self.motor.real_pos)
            name = str(self.motorname_list[i])
            display = name.lower() + "_display"
            line_edit = getattr(self.gui, display, None)
            if line_edit:
                number = round(float(self.motor.real_pos), 6)
                line_edit.setText(str(number))
            else:
                print(display, " not found in the class or its parents")
            i = i + 1



    def movemotor(self):
        motorkey = self.gui.motor_selector.currentText()
        # print(type(self.movesdict))
        mot2move = self.movesdict.get(motorkey) # This should be a Move object, i.e. xmove, ymove, ..., yawmove
        distance = float(self.gui.distance.on_enter_pressed())

        if not self.gui.move_rel.isChecked() and not self.gui.move_abs.isChecked():
            try:
                raise ValueError("Check either Move Rel or Move Abs")
            except ValueError as e:
                QtWidgets.QMessageBox.warning(self, "Error!", str(e))

        elif self.gui.move_rel.isChecked() and not self.gui.move_abs.isChecked():
            mot2move.move_rel(distance = distance )

        elif not self.gui.move_rel.isChecked() and self.gui.move_abs.isChecked():
           mot2move.move_abs(coord = distance)

    def get_speed(self):
        index = self.gui.motor_selector_2.currentIndex()
        # Motors in motor_selector_2 are from user_motorlist, so:

        self.motor = self.user_motorlist[index]
        act_speed = self.motor.getjogspeed()
        act_speed = round(act_speed, 6)
        self.gui.set_display.setText(str(act_speed))

    def set_speed(self):
        index = self.gui.motor_selector_2.currentIndex()
        # Motors in motor_selector_2 are from user_motorlist, so:
        self.motor= self.user_motorlist[index]

        #motor = self.gui.motor_selector_2.itemText(index)

        speed = self.gui.set_display.text()
        #print(speed, type(speed))
        self.motor.setjogspeed(float(speed))
        self.get_speed() # this is just a sanity check...

    def stopall(self):
        message = "#*kill"
        self.shell.send_message(message)
        killed = myWarningBox(title = "Warning!!", message = "All motors killed, /n the Gantry needs a reset & home!")
        killed.show_warning()

    def update_all(self):
        self.update_all_positions()
        if not self.shell.alive:
            self.gui.pmac_display.turn_red()
        elif self.shell.alive:
            self.gui.pmac_display.turn_green()

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
    """def show(self):
        self.show()"""


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MotorControls(None)#20241127 MA: Added None as the class requires the PMAC credentials as parameter.
    window.show()
    sys.exit(app.exec_())
