# Now the fun begins:
import math
import os
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from scipy.ndimage import center_of_mass
from scipy import integrate
import datetime
from ControlCenter.MathUtils import MathUtils

LENSFOCAL = 502.5  # this is the nominal focal length in mm of our lens
ZERO_X = 5280 / 2  # Have to start somewhere, this is half of camera.Width() 2640
ZERO_Y = 4600 / 2  # Have to start somewhere, this is half of camera.Height() 2300


class Measurement():
    f = LENSFOCAL
    X0 = ZERO_X
    Y0 = ZERO_Y

    def __init__(self,

                 nr_of_points=10,  # adding a default seems sane
                 length= 0.0,  # adding a default seems sane
                 nr_of_grabs=5  # adding a default seems sane
                 ):
        # Some sanity values:

        self.length = length  # this is the length (in mm ) of the measurement
        self.points = nr_of_points  # these are the number of measurement points
        self.stepsize = 0.0  # this is the stepsize ( in mm) of the measurement
        self.nrofgrabs = nr_of_grabs  # default nr of camera grabs per measurement point
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

    def slope_calc(self, Y, focal=LENSFOCAL):
        # this is the core of the measurement
        slope_error = 0.5 * (math.atan((2.74 * (  ZERO_Y - Y)) / (focal * 1000)))
        return (slope_error)

    def pretty_printing(self, *arrays):
        """
        Printing data in a decent format for saving.
        :param array1: a 1D np array, size N
        :param array2: a 1D np array, size N
        :return: a tab formatted text, ready to be saved
        """
        if not arrays:
            return ""
        text = ""

        for i in range(len(arrays[0])):
            row = []
            for array in arrays:
                row.append(str(array[i]))
            text += "\t".join(row) + "\n"
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

    def FOP_smoothing(self, arrayX):
        """"
        This function is designed to smooth out the Fuck Off Points (FOP) in the measurement.
        Those points are the ones sticking out of the curve by more than 5 times the RMS.
        The function calculates the average of the 2 point either side of the FOP, and replaces the FOP with the average.

        :param arrayX: an array of slopes.
        :return: an array of smoothed slopes
        """
        smoothed_array = arrayX # first just a copy
        rms = MathUtils.RMS(arrayX)
        topvalue = 4 * rms
        FOP = [] # array of indices of Fuck Off Points
        for i in range(len(arrayX)):
            if arrayX[i] > topvalue:
                FOP.append(i)
        for i in FOP:
            smoothed_array[i] = (arrayX[i - 1] + arrayX[i + 1]) / 2 # substituting the FOPs with the average in the smoothed array.
        return (smoothed_array)

    def compute_spot_intensity(self, ndarray):
        max_index = np.unravel_index(np.argmax(ndarray), ndarray.shape)
        # back_sub = ndarray - np.min(ndarray)
        # ROI definition around the max:
        x_min, x_max = int(max_index[0]) - 150, int(max_index[0]) + 150
        y_min, y_max = int(max_index[1]) - 150, int(max_index[1]) + 150
        roi = ndarray[x_min:x_max, y_min:y_max]
        # subtract background from the Region of Interest
        back_sub = roi - np.min(roi)
        intensity = np.sum(back_sub)
        return(intensity)



    """def figure_error(self, arrayX, arrayY):
        
                Calculates the figure error given and array of positions/slopes
                :param arrayX: y-position of the centroid? or X-position of the head?
                :param arrayY: slopes
                :return: an array, heights.


        heights = np.array([])
        heights = np.cumtrapz(arrayX, arrayY, initial=0)
        return (heights)"""

"""class StabilityMeasurement(Measurement):
    def __init__(self, *args, **kwargs):
        super().__init__():
        self.time_per_point = 1 # 1 second per point
        self.length = 0.0
        self.points = 100 # adding a default seems sane
        self.stepsize = 0.0 # we don't want to move the stage
        self.today = datetime.datetime.now().strftime("%H-%M_%Y%m%d")
        self.directory = os.path.expanduser("~")"""