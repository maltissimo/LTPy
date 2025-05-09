from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QDialog, QVBoxLayout, QLabel, QDialogButtonBox

from Communication import MCG
from Hardware import Source, Motors # , Detector
from ControlCenter.MultiThreading import *

class Utilities():

    def create(my_object, **kwargs):
        if my_object == "shell":
            shell = MCG.Gantry(
                pmac_ip=kwargs.get("pmac_ip"),
                username=kwargs.get("username"),
                password=kwargs.get("password"),
                alive=kwargs.get("alive", False),
                nbytes=kwargs.get("nbytes", 1024),
                echo=kwargs.get("echo", None),
                isinit=kwargs.get("isinit", False)
            )
            return shell

        elif my_object == "util":
            util = Motors.MotorUtil(
                connection=kwargs.get("connection")
            )
            return util

        elif my_object == "laser":
            laser = Source.Laser()
            return(laser)

        elif my_object == "camera":
            camera = Detector.Camera()
            return(camera)

        else:
            raise ValueError("Unknown object type!")

    @staticmethod
    def motors_init( **kwargs):

        if kwargs.get("motorID"):

            motor = Motors.Motor(
                connection = kwargs.get("connection"),
                motorID = kwargs.get("motorID"),
                cs = kwargs.get("cs")
            )
        else:
            motor = Motors.CompMotor(
                connection = kwargs.get("connection"),
                pmac_name = kwargs.get("pmac_name"),
                cs = kwargs.get("cs")
            )
        return motor

    @staticmethod
    def init_moves( **kwargs):
        connection = kwargs.get("connection")
        motor = kwargs.get("motor")
        util = kwargs.get("util")

        move = Motors.Move(connection, motor, util)

        return move

    @staticmethod
    def connect2Pmac():
        connector = Connection_initer()
        PMAC_credentials = connector.get_credentials()

        if not PMAC_credentials:
            cred_warning = myWarningBox("Connection issues", "Connection initialization Cancelled")
            cred_warning.show_warning()
            return

        print(PMAC_credentials)

        try:
            manager = SSHConnectionManager.get_instance(PMAC_credentials)
        except Exception as e:
            conn_warning = myWarningBox(title="Conn error", message=str({e}))
            conn_warning.show_warning()
            return
        return ( manager.get_connection())

class Connection_initer(QWidget):

    """
    This is a graphics class collecting IP, username and password for connecting to the PMAC.
    """
    def __init__(self):
        super().__init__()
        self.ip = None
        self.password = None
        self.username = None

    def get_credentials(self):
        ip, ok = QInputDialog.getText(self, "PMAC Credentials", "Enter PMAC IP address: ")
        if not ok or not ip.strip():
            return None
        self.ip = ip.strip()

        username, ok = QInputDialog.getText(self, "PMAC Credentials", "Enter PMAC Username: ")
        if not ok or not username.strip():
            return None
        self.username = username.strip()

        password= self.password_dialog()
        if password is None:
            return None
        self.password = password

        return {"ip": self.ip, "username": self.username, "password": self.password}

    def password_dialog(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("PMAC Credentials")

        layout = QVBoxLayout()

        label = QLabel("Enter PMAC Password: ")
        layout.addWidget(label)

        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            return password_input.text()
        else:
            return None, False

class SSHConnectionManager:
    _instance = None

    def __init__(self, credentials):
        self.credentials = credentials
        self.connection = None
        self._initialize_connection()

    def _initialize_connection(self):
        self.connection = MCG.Gantry(
            pmac_ip=self.credentials["ip"],
            username=self.credentials["username"],
            password=self.credentials["password"]
        )

        try:
            print("Opening SSH connection...")
            self.connection.openssh()
            print("Connected!")

            print("Initing the PMAC input...")
            self.connection.pmac_init()
            if not self.connection.isinit:
                self.connection.pmac_init()

            self.connection.set_echo()

            print("PMAC Setup complete!")
            print(self.connection.status())

        except Exception as e:
            raise RuntimeError(f"Failed to initialize PMAC connection: {e}")

    @classmethod
    def get_instance(cls, credentials):
        if cls._instance is None:
            cls._instance = SSHConnectionManager(credentials)
        return cls._instance

    def get_connection(self):
        return self.connection


