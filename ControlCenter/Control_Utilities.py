from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from scipy.ndimage import center_of_mass
import numpy as np
from Communication import MCG
from Hardware import Source, Motors  # , Detector


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

class Connection_initer(QWidget):
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


class MathUtils():

    def um2mm( umvalue):
        # converts microns to mm
        return (umvalue / 1000)

    def mm2um(mmvalue):
        # converts mm to microns
        return (mmvalue * 1000)

    def fwhm(self, nparrayX, nparrayY):
        """
        Returns the FWHM of a 1D array. If a peak is defined in X-y Coordinates, then
        finds the right and left most indexes of the half max of hte peak,
        then compute the nparrayX full width from those indexes
        The return value is in the units of nparrayX.
        """

        halfmax = np.max(array)/2# this finds the halfmax  of the array
        #takes the 'derivative' of signum(halfmax - array[])
        d = np.sign(halfmax - array[0:-1]) - np.sign(halfmax - array[1:])
        # find the right and left most indexes:
        left_index = np.where(d > 0)[0]
        right_index = np.where(d < 0 )[-1]
        FWHM = nparrayX[right_index] - nparrayX[left_index]

        return FWHM

    def splitimage(self, 2DnpArray):
        """"
        This is used to provide arrays of a laser image (i.e. a spot).
        First, it finds the centroid of the spot, which provides X and Y pixel indexes of where the
        centroid of the image can be found.
        Then it splits the 2D array along those coordinates, returning 2, 1D vectors

        """
        centroid = center_of_mass(2DnpArray)

        Y_vector = 2DnpArray[int(centroid[0]), :]
        X_vector = 2DnpArray[:,int(centroid[1])]

        return(X_vector, Y_vector)

    def calc_2D_fwhm(self, 2darray):

        HOR_vector, VER_vector = self.splitimage(2darray)
        HOR_axis = np.arange(0, len(HOR_vector), 1)
        VER_axis = np.arange(0, len(VER_vector), 1)

        HOR_FWHM = self.fwhm(HOR_axis, HOR_vector)
        VER_FWHM = self.fwhm(VER_axis, VER_vector)

        return(HOR_FWHM, VER_FWHM)





    
