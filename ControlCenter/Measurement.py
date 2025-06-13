# Now the fun begins:
import math
import os
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from scipy.ndimage import center_of_mass
from scipy import integrate
import datetime

LENSFOCAL = 502.5  # this is the nominal focal length in mm of our lens
ZERO_X = 5280 / 2  # Have to start somewhere, this is half of camera.Width() 2640
ZERO_Y = 4600 / 2  # Have to start somewhere, this is half of camera.Height() 2300


class Measurement():
    f = LENSFOCAL
    X0 = ZERO_X
    Y0 = ZERO_Y

    def __init__(self,

                 nr_of_points=10,  # adding a default seems sane
                 length=1,  # adding a default seems sane
                 nr_of_grabs=5  # adding a default seems sane
                 ):
        # Some sanity values:

        self.length = 0.0  # this is the length (in mm ) of the measurement
        self.points = 0  # these are the number of measurement points
        self.stepsize = 0.0  # this is the stepsize ( in mm) of the measurement
        self.nrofgrabs = 5  # default nr of camera grabs per measurement point
        self.xStartPos = 650000  # default @ middle of stage travel...
        self.today = datetime.datetime.now().strftime("%H-%M_%Y%m%d")
        self.directory = os.path.expanduser("~") # selecting the default directory as users home directory

        self.slopes_rms = 0.0
        self.heights_rms = 0.0

    def get_save_directory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        options |= QFileDialog.ShowDirsOnly

        self.directory = QFileDialog.getExistingDirectory(
            None,
            "Select Directory",
            os.path.expanduser("~"),
            options = options
        )
        #print(self.directory)

    def save_data(self, filename, text):
        if self.directory:
            filename = os.path.join(self.directory, filename)
            with open(filename, "w", encoding="ASCII") as f:
                f.write(text)
        else:
            print("No directory selected")

    def slope_calc(self, Y):
        # this is the core of the measurement
        slope_error = 0.5 * (math.atan((2.74 * (  ZERO_Y - Y)) / (LENSFOCAL * 1000)))

        """print("Inside the slope_calc loop Y: ", Y)
        print("Inside the slope_calc loop ZERO_Y ", ZERO_Y)
        print("Inside the slope_calc loop focal: ", LENSFOCAL, "\t", LENSFOCAL * 1000)
        print("inside the slope_calc loop, (Y - ZERO_Y): ", 2.74 * (Y - ZERO_Y))
        print("inside the slope_calc loop, math.atan(Y - ZERO_Y): ", math.atan(2.74* (Y - ZERO_Y)))
        print("Inside the slope_calc loop slope: ", slope_error)"""
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

    def height_calc(self, arrayY, arrayX):
        """
                Calculates the figure error given and array of positions/slopes. Given the nature of the method,
                it needs a full array, the method must be called over a fully-formed slopes array.
                see:
                http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.integrate.cumtrapz.html
                :param arrayY: slopes, value to be integrated
                :param arrayX: Coordinate to integrate along, optional.
                :return: an array, heights.
                """

        heights = np.array([])
        heights = integrate.cumtrapz(arrayY, arrayX, initial=0)
        return (heights)



    def figure_error(self, arrayX, arrayY):
        """
                Calculates the figure error given and array of positions/slopes
                :param arrayX: y-position of the centroid? or X-position of the head?
                :param arrayY: slopes
                :return: an array, heights.


        heights = np.array([])
        heights = np.cumtrapz(arrayX, arrayY, initial=0)
        return (heights)"""

