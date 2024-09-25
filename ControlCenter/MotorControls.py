import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow

from ControlCenter.Control_Utilities import Utilities as Uti
from Graphics.Base_Classes_graphics import Motors_GUI
from Hardware.Motors import MotorUtil


class MotorControls(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create an instance of the Motors.GUI class:

        self.gui = Motors_GUI()
        self.gui.setupUi(self)

        self.movesdict = {}

        self.username = None
        self.pmac_ip = "127.0.0.200" # adding a default for safety.
        self.password = None
        self.shell = Uti.create(self, my_object="shell", pmac_ip=self.pmac_ip, username=self.username,
                                      password=self.password)
        self.util = Uti.create(self, my_object="util",
                                     connection=self.shell)  # Instantiating an object of MotorUtil class
        self.full_motorslist = []
        self.user_motorslits = []
        self.init_motors()
        self.allMotors_inited = False
        self.allMoves_inited = False

        # Timer for updating:
        self.timer = QTimer(self)
        #self.timer.timeout.connect(self.update_positions) moved inside the update_all method
        self.timer.start(50)  # updating every 200 ms
        self.timer.timeout.connect(self.update_all) # connects to the update_all method

        #Connect the various bits in the UI:

        self.gui.moveButton.clicked.connect(self.movemotor())
        # This line here below connects to the PMAC.
        self.gui.connect.clicked.connect(self.Connect2_Pmac())

        try:
            self.gui.ResetAll.clicked.connect(MotorUtil.resetGantry)
            if not self.shell.alive:
                raise ConnectionError("No connection to PMAC")
            QtWidgets.QMessageBox.warning("System reset!")
        except ConnectionError as e:
            QtWidgets.QMessageBox.warning(self, "Connection Error: ", str(e))

        try:
            self.gui.HomeGantry.clicked.connect(MotorUtil.homeGantry)
            if not self.shell.alive:
                raise ConnectionResetError("No connection to PMAC")
            self.gui.sh_display.turn_green()
            QtWidgets.QMessageBox.warning("System homed!")
        except ConnectionError as e:
            QtWidgets.QMessageBox.warning(self, "Connection Error", str(e))

        self.gui.stopButton.clicked.connect(self.stopall)
        self.gui.setspeed.clicked.connect(self.get_speed)

        self.gui.getspeed.clicked.connect(self.set_speed)

        self.gui.motor_selector.currentIndexChanged.connect(self.update_units)
        self.gui.motor_selector_2.currentIndexChanged.connect(self.update_units)
        # Used twice, so that if a user changes in one tab, the other is automatically changed by the update_units method

        self.gui.distance.returnPressed.connect(self.update_distance)
        # TODO:
        #       - update_all implementation


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
        try:
            motor1 = Utilities.motors_init(connection = self.shell, motorID = 1, cs = 1)
            motor2 = Utilities.motors_init(connection=self.shell, motorID=2, cs=1)
            motor3 = Utilities.motors_init(connection=self.shell, motorID=3, cs=1)
            yaw = Utilities.motors_init(connection= self.shell, motorID=4, cs=2)
            X = Utilities.motors_init(connection= self.shell, motorID=5, cs=3)
            Y = Utilities.motors_init(connection= self.shell, motorID=6, cs=3)

            Z = Utilities.motors_init(connection = self.shell, pmac_name = "Z", cs = 1)
            pitch = Utilities.motors_init(connection = self.shell, pmac_name = "B", cs = 1)
            roll = Utilities.motors_init(connection = self.shell, pmacn_name = "A", cs = 1)


            if self.shell is None or self.shell.alive == False or self.shell.isinit == False:
                raise ValueError ("Pmac not connected or not correctly inited!")

            self.allMotors_inited = True
            self.full_motorslist = [
                motor1,
                motor2,
                motor3,
                yaw,
                X,
                Y,
                Z,
                pitch,
                roll
            ]

            self.user_motorslits = [
                X,
                Y,
                Z,
                pitch,
                roll,
                yaw
            ]
            self.init_moves()

            QtWidgets.QMessageBox.warning(self, "All motors correctly initialized!")

            #Filling the data for comboboxes:

            for motor in self.user_motorslits:
                self.motor_selector_2.addItem((str(motor)))
                self.motor_selector.addItem(str(motor))

        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "ERROR!", str(e))
        return(X, Y, Z, pitch, roll, yaw, motor1, motor2, motor3)

    def init_moves(self):
        try:
            xmove = Utilities.init_moves(connection = self.shell, motor = X)
            ymove = Utilities.init_moves(connection=self.shell,  motor = Y)
            zmove = Utilities.init_moves(connection = self.shell, motor = Z)
            pitchmove = Utilities.init_moves(connection = self.shell, motor = pitch)
            rollmove = Utilities.init_moves(connection = self.shell, motor = roll)
            yawmove = Utilities.init_moves(connection = self.shell, motor = yaw)
            if self.shell is None or self.shell.alive == False or self.shell.isinit == False:
                raise ValueError("Pmac not connected or not correctly inited!")
            self.allMoves_inited = True
            self.movesdict = self.update_dict()
        except ValueError as e:
            QtWidgets.QMessageBox(self, "Error!", str(e))

        QtWidgets.QMessageBox.warning(self, "Moves correctly initialized!")

    def update_dict(self):
        self.movesdict = {"X": xmove,
                          "Y": ymove,
                          "Z": zmove,
                          "pitch": pitchmove,
                          "roll": rollmove,
                          "yaw": yawmove
                          }

    def update_units(self):
        """
        this methods is used to change the labels displaying the units of measurement in the Motors and the Utilities tab
        :return:
        """
        index = self.gui.motor_selector.currentIndex
        if index <= 2:
            self.gui.units.setText("µm") # units is the name of the label in  the Motors tab
            self.gui.label.setText("µm") # label is the name of the label in the Utilities tab
        elif index > 2:
            self.gui.label.setText("degrees") # label is the name of the label in the Utilities tab
            self.gui.units.setText("degrees") # units is the name of the label in  the Motors tab

    def set_motorlist(self):
        self.user_motorslits = [
            X.motorname,
            Y.motorname,
            Z.pmac_name,
            "pitch",
            "roll",
            yaw.motorname
        ]

    def update_distance (self):
        index = self.gui.motor_selector_2.currentIndex
        if index <= 2:
            self.gui.label.setText("µm")
        elif index >2:
           self.gui.label.setText ("degrees")

    def update_positions(self):
        for motor in self.user_motorslits:
            motor.real_pos = self.motor.get_real_pos()

    def movemotor(self):
        motorkey = self.gui.motor_selector.currentText()
        mot2move = self.movesdict.get(motorkey) # This should be xmove, ymove, ..., yawmove
        distance = float(self.gui.distance.returnPressed())

        if not self.gui.move_rel.isChecked() and not self.gui.move_abs.isChecked():
            try:
                raise ValueError("Check either Move Rel or Move Abs")
            except ValueError as e:
                QtWidgets.QMessageBox.warning(self, "Error!", str(e))

        elif self.gui.move_rel.isChecked() and not self.gui.move_abs.isChecked():
            mot2move.gui.move_rel(distance = distance )

        elif not self.gui.move_rel.isChecked() and self.move_abs.isChecked():
           mot2move.gui.move_abs(distance = distance)

    def get_speed(self):
        index = self.gui.motor_selector_2.currentIndex()
        motor = self.gui.motor_selector_2.itemText(index)
        act_speed = motor.getjogspeed()
        act_speed = round(act_speed, 6)
        self.gui.set_display.setText(str(act_speed))

    def set_speed(self):
        index = self.gui.motor_selector_2.currentIndex()
        motor = self.gui.motor_selector_2.itemText(index)
        speed = self.gui.distance.text()
        motor.setjogspeed()
        self.get_speed() # this is just a sanity check...

    def stopall(self):
        message = "#*kill"
        self.shell.send_message(message)
        QtWidgets.QMessageBox.warning("All motors killed")

    def update_all(self):
        self.update_positions()
        if not self.shell.alive:
            self.gui.pmac_display.turn_red()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MotorControls()
    window.show()
    sys.exit(app.exec_())

