# Now the fun begins:
import math
import os
import numpy as np
from scipy.ndimage import center_of_mass
from scipy import integrate

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
        self.nr_of_points = nr_of_points
        self.length = length  # length of measurement, units in mm. Must be converted to µm, as that's the unit of X.

        self.images = []
        self.stepsize = self.length / self.nr_of_points
        self.slopes_rms = 0.0
        self.heights_rms = 0.0

    def save_data(self, filename, text):
        """directory = os.path.dirname(filename)
        if directory and not os.path.exists(filename):
            os.makedirs(directory)"""
        # filename = "data of " + TODAY + ".txt"
        with open(filename, "w", encoding="ASCII") as f:
            f.write(text)
        # print("Data saved into: " + filename )

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

