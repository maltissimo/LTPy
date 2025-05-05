from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt5.QtCore import QMutex, QMutexLocker, QWaitCondition

import ControlCenter.Control_Utilities
from Communication import MCG
from Hardware import Source, Motors # , Detector
from scipy.ndimage import center_of_mass
import numpy as np
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
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
timer = Qtimer()
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


class CoordMessenger():
    """
    This class is intended to act as a multi-threading messenger to and from the Gantry.
    The goal is JUST to receive motor coordinates, and to pass those as a dictionary out.

    """

    def __init__(self, connection, sleep_time=51):
        self.worker = WorkerThread(task=self.get_and_update_coords, sleep_time=sleep_time)
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()
        self.paused = False
        self.connection = connection

        if not self.connection or self.connection.alive == False:
            conn_warning = myWarningBox(title="Warning!",
                                        message="PMAC Connection not active!")
            conn_warning.show_warning()

        self.coordinates = {
            "X": 0.0,
            "Y": 0.0,
            "Z": 0.0,
            "pitch": 0.0,
            "roll": 0.0,
            "yaw": 0.0
        }

        self.worker.update_signal.connect(self.update_coordinates)
        self.worker.end_signal.connect(self.stop)
        self.worker.begin_signal.connect(self.start)
        self.worker.error_signal.connect(self.handleworkererror)

    def get_and_update_coords(self):
        self.mutex.lock()
        while self.paused:
            self.pause_condition.wait(self.mutex)
        self.mutex.unlock()
        self.connection.send_receive("&1,2,3p")
        response = self.connection.textoutput
        #print(response)

        return(response)

    def update_coordinates(self, response):
        flag = 0
        #print("update method called, with result: ", response)
        response = list(response)
        if not response:
            return
        try:
            """if response[0] != '&1,2,3p':
                print("full Response: ", response)
                flag =1"""
            while response and response[0] != '&1,2,3p':
                response.pop(0)
            """ The two lines above clean the PMAC response, so that only coordinates are received. """
            """if flag == 0:
                print("Cleaned response: ", response)
                flag = 0"""
            if len(response) < 4:
                return # this avoids crashes from not-well formed responses. since the update is rapid this should not be an issue
            CS1 = response[1].split()
            CS2 = response[2].split()
            CS3 = response[3].split()
            #print("CS1: " + str(CS1) + "\nCS2 : " +str(CS2) + "\nCS3: " + str(CS3))
            with QMutexLocker(self.mutex):
                self.coordinates.update({
                    "pitch" : float(CS1[1][1:]),
                    "roll": float(CS1[0][1:]),
                    "Z": float(CS1[2][1:]),
                    "yaw": float(CS2[0][1:]),
                    "X": float(CS3[0][1:]),
                    "Y": float(CS3[1][1:])
                })
                """for key in self.coordinates :
                    print(key, self.coordinates[key])"""

        except ValueError as e:
            get_coord_warning = myWarningBox(title="Error",
                                         message=str(e))
            get_coord_warning.show_warning()
    def pause(self):
        self.worker.pause()
    def resume(self):
        self.worker.resume()

    def start(self):
        if not self.worker.isRunning():
            self.worker.start()

    def stop(self):
        self.worker.stop()

    def handleworkererror(self, message):
        worker_warning = myWarningBox(title="Error",
                                      message=str(message))
        worker_warning.show_warning()

class MoveMessenger():
    """
    This class is intended to multi-thread move commands to the PMAC, in order to speedup
    the GUI.
    """
    def __init__(self, connection, sleep_time = 100):
        self.worker = WorkerThread(task = move_motor, sleep_time = sleep_time)
        self.mutex = QMutex
        self.connection = connection

        if not self.connection or self.connection.alive == False:
            conn_warning = myWarningBox(title = "Warning!",
                                        message = "PMAC Connection not active!")
            conn_warning.show_warning()
