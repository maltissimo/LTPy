import pypylon.pylon as py
import numpy as np
"""
Contains all the info necessary for the communication between Mainc Computer (MC) and CMOS detector (Det)

"""
class Camera(py.InstantCamera):
    def __init__(self, mycam = None, MyExpTime = 0):
        self.mycam = self.py.TlFactory.GetInstance().CreateFirstDevice()
        self.MyExpTime = self.ExposureTime.Min

    def InitCam(self):
        """
        this takes about 300 ms once it is called, but its called only once during execution, so the overhead is acceptable.
        The Camera is OPen in the function, so it's ready fo ruse.
        The camera is also initialied wvia the UserSetSelector method, and the exposure time is set to the minimum allowable,
        i.e. 12 microseconds.

        :return:
        """
        self.UserSetSelector ="Default"
        self.UserSetLoad.Execute()
        self.ExposureTime = self.ExposureTime.Min





