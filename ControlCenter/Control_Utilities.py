from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QDialog, QVBoxLayout, QLabel, QDialogButtonBox

from Communication import MCG
from Hardware import Source, Motors # , Detector
from scipy.ndimage import center_of_mass
import numpy as np

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

    @staticmethod
    def um2mm( umvalue):
        # converts microns to mm
        return (umvalue / 1000)

    @staticmethod
    def mm2um(mmvalue):
        # converts mm to microns
        return (mmvalue * 1000)

    @staticmethod
    def fwhm( nparray):
        """
        Returns the FWHM of a 1D array. If a peak is defined in X-y Coordinates, then
        finds the right and left most indexes of the half max of hte peak,
        then compute the nparrayX full width from those indexes
        The return value is in the units of nparrayX.
        """

        halfmax = np.max(nparray) / 2  # this finds the halfmax  of the array
        above_half = nparray >= halfmax
        indexes = np.where(above_half)[0]
        FWHM = indexes[-1] - indexes[0]
        """d = np.sign(halfmax - nparrayY[0:-1]) - np.sign(halfmax - nparrayY[1:])
        # find the right and left most indexes:
        left_index = np.where(d > 0)[0]
        right_index = np.where(d < 0)[-1]
        FWHM = nparrayX[right_index] - nparrayX[left_index]"""

        return FWHM

    @staticmethod
    def centroid( ndarray):
        """
        this had to be modified from a simple scipy.center_of_mass, as it doesn't track correctly the spot center.
        centroid = center_of_mass(ndarray)
        return(np.array(centroid))

        :param ndarray:
        :return:
        """
        max_index = np.unravel_index(np.argmax(ndarray), ndarray.shape)
        back_sub = ndarray - np.min(ndarray)
                #ROI definition around the max:
        x_min, x_max = int(max_index[0]) - 150, int(max_index[0]) + 150
        y_min, y_max = int(max_index[1]) - 150, int(max_index[1]) + 150
        roi = back_sub[x_min:x_max, y_min:y_max]
        com_roi = (center_of_mass(roi))
                #print("this is the Center of Mas ROI: ", com_roi)
        com_global = (int(com_roi[0]) + x_min, int(com_roi[1]) + y_min)
                #print(com_global[0], com_global[1])
                
        return (com_global)





    @staticmethod
    def splitimage( nparray2D):
        """"
        This is used to provide arrays of a laser image (i.e. a spot).
        First, it finds the centroid of the spot, which provides X and Y pixel indexes of where the
        centroid of the image can be found.
        Then it splits the 2D array along those coordinates, returning 2, 1D vectors

        """
        center = MathUtils.centroid(nparray2D)
        centerX, centerY = np.round(center).astype(int)
        #print(centerX, centerY)

        X_vector = nparray2D[centerX, :]
        Y_vector = nparray2D[:, centerY]

        return (X_vector, Y_vector)

    @staticmethod
    def calc_2D_fwhm(nparray2D):
        HOR_vector, VER_vector = MathUtils.splitimage(nparray2D)
        """HOR_axis = np.arange(0, len(HOR_vector), 1)
        VER_axis = np.arange(0, len(VER_vector), 1)"""

        HOR_FWHM = MathUtils.fwhm(HOR_vector)
        VER_FWHM = MathUtils.fwhm(VER_vector)

        return (HOR_FWHM, VER_FWHM)

    @staticmethod
    def my_fit(arrayX, arrayY, order):
        """

        :param arrayX: typically, an array with the step positions of the measurement
        :param arrayY: array of values to be fit
        :param order: order of the polynomial fit
        :return: an array of fitted data and the radius of the sphere as the 0-th order coefficient of the fit
        """

        coeff = np.polyfit(arrayX, arrayY, order)
        p = np.poly1d(coeff)
        fit = p(arrayX)
        radius = 1 / coeff[0]
        #print("Radius as coeff[0], in m: ", radius/1000000)
        return (fit, radius)

    @staticmethod
    def RMS(array):
        """
        calculates the root mean square value of any array
        :param array: input array for which the RMS calculation is needed
        :return: an RMS value, same units as array.
        """
        """mysum = np.sum(array)
        nr_of_points = len(array)"""
        RMS = np.sqrt(np.mean(array**2))
        return (RMS)

    @staticmethod
    def is_float(string):
        try:
            float(value)
            return True
        except ValueError:
            return False
