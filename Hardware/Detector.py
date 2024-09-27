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

    def __init__(self): #,MyExpTime = 6, minexptime = 0, maxexptime = 0,  grab_nr = 10, isopen = False, height = 1400, width = 1400, gain = 0.0"""):

        self.camera= py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
        """if self.camera is not None: 
            self.MyExpTime = self.camera.ExposureTime
            self.minexptime = self.camera.ExposureTime.Min
            self.maxexptime = self.camera.ExposureTime.Max
            self.height = self.camera.Height.Value
            self.width = self.camera.Width.Value
            self.gain = self.camera.Gain
        else:
            self.MyExpTime = MyExpTime # set to 6 µseconds
            self.minexptime = minexptime
            self.maxexptime = maxexptime
            self.grab_nr = grab_nr
            self.height = height
            self.width = width
            self.gain = gain"""
        """self.opencam"""
        self.camera.StartGrabbing(py.GrabStrategy_LatestImageOnly)
        self.frame = None

    def __str__(self):
        return f"Basler camera: Exposure time = {self.camera.ExposureTime}, default nr of frames to grab = {self.grab_nr}, \
                Image Height = {self.camera.Height.Value}, Image Width = {self.camera.Width.Valye}"

    def getHeight(self):
        return(self.camera.Height.Value)

    def getWidth(self):
        return (self.camera.Width.Value)

    def opencam(self):
        """
        this takes about 300 ms once it is called, but its called only once during execution, so the overhead is acceptable.
        The Camera is OPen in the function, so it's ready fo ruse.
        The camera is also initialied via the UserSetSelector method, and the exposure time is set to the minimum allowable,
        i.e. 12 microseconds.

        :return:
        """
        self.camera.UserSetSelector = "Default"
        self.camera.UserSetLoad.Execute()
        self.camera.ExposureTime = 12
        self.isopen = self.camera.IsOpen()
        self.height = self.camera.getHeight()
        self.width = self.camera.getWidth()
        self.minexptime = self.camera.ExposureTime.Min
        self.maxexptime = self.camera.ExposureTime.Max

    def closecam(self):
        self.camera.Close()
        self.isopen = self.camra.IsOpen()

    def acquire_once(self):
        res = self.camera.GrabOne(1000)
        myimage = res.GetArray() #this transforms res into and ndarray for further processing.
        return(myimage)

    def grabdata(self):
        if self.camera.IsGrabbing():
            res = self.camera.RetrieveResult(5000, py.TimeoutHandling_ThrowException)
            """ with camera.RetrieveResult(100) as res:"""
            if res.GrabSucceeded():
                self.frame = res.Array
            res.Release()
    def set_exp_time(self, custom_time):
        """
        Sets the Camera exposure time, units are in microseconds. Default is 6 µs, to be changed by user

        :param custom_time: Desired exposure time in microseconds
        :return:
        """
        if custom_time < 6:
            custom_time = 6
        elif custom_time > self.camera.ExposureTime.Max:
            custom_time = self.camera.ExposureTime.Max
        self.camera.ExposureTime = custom_time
        #self.MyExpTime = self.camera.ExposureTime()

    def set_grab_nr(self, mynewgrabnumber = 10 ):
        self.grab_nr = mynewgrabnumber

    def set_gain(self, gain ):
        self.camera.Gain = gain
        #self.gain = self.camera.Gain

