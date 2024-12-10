# Now the fun begins:
import math
import os
import numpy as np
from scipy.ndimage import center_of_mass

LENSFOCAL = 500  # this is the nominal focal length in mm of our lens
ZERO_X = 5280 / 2  # Have to start somewhere, this is half of camera.Width()
ZERO_Y = 4600 / 2  # Have to start somewhere, this is half of camera.Height()


class Measurement():
    f = LENSFOCAL
    X0 = ZERO_X
    Y0 = ZERO_Y

    def __init__(self,

                 nr_of_points=10,  # adding a default seems sane
                 length=1,  # adding a default seems sane
                 nr_of_grabs=5  # adding a default seems sane
                 ):
        self.nr_of_points = nr_of_points
        self.length = length  # length of measurement, units in mm. Must be converted to µm, as that's the unit of X.
        """
        self.motor1 = motor1
        self.motor2 = motor2
        self.motor3 = motor3
        self.xmotor = X
        self.xmove = xmove

        self.ymotor = Y
        self.ymove = ymove
        self.zmotor = Z
        self.zmove = zmove
        self.pitch = pitch
        self.pitchmove = pitchmove
        self.roll = roll
        self.rollmove = rollmove
        self.yaw = yaw
        self.yawmove = yawmove"""

        self.images = []
        self.stepsize = self.length / self.nr_of_points
        self.results = ""

        """
        self.camera = camera
        self.nr_of_grabs = nr_of_grabs
        """

        """ self.x_start_pos = self.X.get_real_pos()
        self.y_start_pos = self.Y.get_real_pos()
        self.z_start_pos = self.Z.get_real_pos()
        self.pitch_start_pos = self.pitch.get_real_pos()
        self.roll_start_post = self.roll.get_real_pos()
        self.yaw_start_pos = self.yaw.get_real_pos()"""

    def centroid(self, ndarray):
        return center_of_mass(ndarray)

    def save_data(self, filename, text):
        """directory = os.path.dirname(filename)
        if directory and not os.path.exists(filename):
            os.makedirs(directory)"""
        # filename = "data of " + TODAY + ".txt"
        with open(filename, "w", encoding="ASCII") as f:
            f.write(text)
        # print("Data saved into: " + filename )

    def slope_calc(self, Y, Y0, f):
        # this is the core of the measurement
        slope_error = 0.5 * (math.atan(Y - Y0)) / f * 1000
        return (slope_error)

    def pretty_printing(self, array1, array2):
        """
        Printing data in a decent format for saving.
        :param array1: a 1D np array, size N
        :param array2: a 1D np array, size N
        :return: a tab formatted text, ready to be saved
        """
        text = ""
        for i in range(len(array1)):
            text += str(array1[i]) + "\t" + str(array2[i]) + "\n"
        return (text)

    def height_calc(self):
        pass

    def sphere_fit(self, arrayX, arrayY):
        coeff = np.polyfit(arrayX, arrayY, 1)
        p = np.poly1d(coeff)
        fit = np.polyval(p, arrayX)
        radius = 1 / coeff[0]
        return (radius)

    def RMS(self, array):
        """
        calculates the root mean square value of any array
        :param array: input array for which the RMS calculation is needed
        :return: an RMS value, same units as array.
        """
        mysum = np.sum(array)
        nr_of_points = len(array)
        RMS = np.sqrt(mysum * mysum) / nr_of_points
        return (RMS)

    def figure_error(self, arrayX, arrayY):
        """
        Calculates the figure error given and array of positions/slopes
        :param arrayX: y-position of the centroid? or X-position of the head?
        :param arrayY: slopes
        :return: an array, heights.
        """

        heights = []
        heights = np.cumtrapz(arrayX, arrayY, initial=0)
        return (heights)
