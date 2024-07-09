import pypylon.pylon as py
import numpy as np
"""
Contains all the info necessary for the communication between Mainc Computer (MC) and CMOS detector (Det)

"""
class Camera:

    """
    This class overloads some of hte methods provided inside pypylon. The available methods will be updated as soon as
    they become necessary for the operations of the LTP.
    For a comprehensive training on Pypylon see:

    https://www.youtube.com/watch?v=ZWA5fRp0mSk

    provided by Basler.

    03/07/2024

    """

    def __init__(self, MyExpTime = 6, minexptime = 0, maxexptime = 0,  grab_nr = 10, isopen = False, height = 1400, width = 1400, gain = 0.0):

        self.camera= py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())

        self.MyExpTime = MyExpTime # set to 6 µseconds
        self.minexptime = minexptime
        self.maxexptime = maxexptime
        self.grab_nr = grab_nr
        self.isopen = isopen
        self.height = height
        self.width = width
        self.gain = gain

    def __str__(self):
        return f"Basler camera: Exposure time = {self.MyExpTime}, default nr of frames to grab = {self.grab_nr}, \
                Image Height = {self.height}, Image Widht = {self.width}"

    def getHeight(self):
        return(self.Height.Value)

    def getWidth(self):
        return (self.Width.Value)

    def opencam(self):
        """
        this takes about 300 ms once it is called, but its called only once during execution, so the overhead is acceptable.
        The Camera is OPen in the function, so it's ready fo ruse.
        The camera is also initialied via the UserSetSelector method, and the exposure time is set to the minimum allowable,
        i.e. 12 microseconds.

        :return:
        """
        self.UserSetSelector ="Default"
        self.UserSetLoad.Execute()
        self.ExposureTime = self.ExposureTime.Min
        self.open = self.Open()
        self.isopen = self.IsOpen()
        self.height = self.getHeight()
        self.width = self.getWidth()
        self.minexptime = self.ExposureTime.Min
        self.maxexptime = self.ExposureTime.Max

    def closecam(self):
        self.Close()
        self.isopen = self.IsOpen()

    def acquire_once(self):
        res = self.GrabOne(1000)
        myimage = res.GetArray() #this transforms res into and ndarray for further processing.
        return(myimage)

    def grabdata(self):
        img_sum = np.zeros((self.height, self.width), dtype = np.uint16)
        self.camera.StartGrabbingMax(100 * self.grab_nr)
        self.camera.StopGrabbing()
        while self.camera.IsGrabbing():
            with self.camera.RetrieveResult(1000) as res: # the 1000 is the timeout in ms.
                if res.camera.GrabSucceded():
                    img = res.Array
                    img_sum += img
                else:
                    raise RuntimeError("Grab Failed")
        self.camera.StopGrabbing()

        return(img_sum)

    def set_exp_time(self, custom_time = 6 ):
        """
        Sets the Camera exposure time, units are in microseconds. Default is 6 µs, to be changed by user

        :param custom_time: Desired exposure time in microseconds
        :return:
        """
        self.ExposureTime = custom_time
        self.MyExpTime = self.ExposureTime()

    def set_grab_nr(self, mynewgrabnumber = 10 ):
        self.grab_nr = mynewgrabnumber

    def set_gain(self, gain ):
        self.Gain = gain
        self.gain = self.Gain

