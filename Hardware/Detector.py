import pypylon.pylon as py

from ControlCenter import MathUtils
import threading

"""
Contains all the info necessary for the communication between Main Computer (MC) and CMOS detector (Det)

"""
class Camera:

    """
    This class overloads some of hte methods provided inside pypylon. The available methods will be updated as soon as
    they become necessary for the operations of the LTP.
    For a comprehensive training on Pypylon see:

    https://www.youtube.com/watch?v=ZWA5fRp0mSk

    provided by Basler.

    03/07/2024

    Pixel size is:

    2.74um x 2.74 um

    12/10/2024

    """

    def __init__(self): #,MyExpTime = 6, minexptime = 0, maxexptime = 0,  grab_nr = 10, isopen = False, height = 1400, width = 1400, gain = 0.0"""):

        self.camera= py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
        if self.camera is not None:
            self.opencam()
            self.MyExpTime = self.camera.ExposureTime
            """self.minexptime = self.camera.ExposureTime.Min
            self.maxexptime = self.camera.ExposureTime.Max"""
            self.height = self.camera.Height()
            self.grab_nr = 5
            self.width = self.camera.Width()
            self.gain = self.camera.Gain()
        else:
            self.MyExpTime = 6.0  # set to 6 µseconds
            self.minexptime = 0.0
            self.maxexptime = 50.0
            self.grab_nr = grab_nr
            self.height = height
            self.width = width
            self.gain = gain

        self.frame = None
        self.camera_lock = threading.Lock()

    def __str__(self):
        return f"Basler camera: Exposure time = {self.camera.ExposureTime()}, default nr of frames to grab = {self.grab_nr}, \
                Image Height = {self.camera.Height()}, Image Width = {self.camera.Width()}"

    def getHeight(self):
        return(self.camera.Height())

    def getWidth(self):
        return (self.camera.Width())

    def opencam(self):
        """
        this takes about 300 ms once it is called, but its called only once during execution, so the overhead is acceptable.
        The Camera is OPen in the function, so it's ready fo ruse.
        The camera is also initialied via the UserSetSelector method, and the exposure time is set to the minimum allowable,
        i.e. 12 microseconds.

        :return:
        """
        self.camera.Open()
        self.camera.UserSetSelector = "Default"
        self.camera.UserSetLoad.Execute()
        self.camera.PixelFormat = "Mono8" #Use Mono12 if switching to Matplotlib. CV2 seems to be more responsive.
        self.camera.ExposureTime = 8.0
        self.isopen = self.camera.IsOpen()
        self.height = self.camera.Height()  # 4600 pixels
        self.width = self.camera.Width()  # 5280 pixels
        self.x_pixel_size = 2.74 # this is in microns
        self.y_pixel_size = 2.74 # this is in microns
        self.minexptime = self.camera.ExposureTime.Min
        self.maxexptime = self.camera.ExposureTime.Max
        self.isopen = self.camera.IsOpen()

    def closecam(self):
        self.camera.Close()
        self.isopen = self.camera.IsOpen()


    def acquire_once(self):
        res = self.camera.GrabOne(1000)
        if res.GrabSucceeded():
            self.frame = res.Array #this transforms res into and ndarray for further processing.
        res.Release()
        return(self.frame)

    def start_continuous_grabbing(self):
        if not self.camera.IsGrabbing():
            self.camera.StartGrabbing(py.GrabStrategy_LatestImageOnly, py.GrabLoop_ProvidedByUser)

    def grabdata(self, ensure_started = True):
        if ensure_started and not self.camera.IsGrabbing():
            self.camera.StartGrabbing(py.GrabStrategy_LatestImageOnly, py.GrabLoop_ProvidedByUser)
        try:
            res = self.camera.RetrieveResult(25, py.TimeoutHandling_ThrowException)  #tested a few values, 25 seems the minimum
            if res.GrabSucceeded():
                self.frame = res.Array
                res.Release()
                return self.frame
            else:
                res.Release()
                return None
        except py.TimeoutHandling_ThrowException:
            return None # this takes care of the possibility of a timeout.
        except Exception as e:
            print (f"[Camera grabdata] Error :{e}")
            return None

        """"### MY OLD CODE HERE BELOW
        if not self.camera.IsGrabbing():
            self.camera.StartGrabbing(py.GrabStrategy_LatestImageOnly)
        res = self.camera.RetrieveResult(100, py.TimeoutHandling_ThrowException)
        if res.GrabSucceeded():
            self.frame = res.GetArray()
        res.Release()
        #self.camera.StopGrabbing()
        return(self.frame)"""

    def stop(self):
        if self.camera.IsGrabbing():
            self.camera.StopGrabbing()

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
        # self.MyExpTime = self.camera.ExposureTime()


    def set_grab_nr(self, mynewgrabnumber=5):
        self.grab_nr = mynewgrabnumber

    def set_gain(self, gain ):
        self.camera.Gain = gain
        #self.gain = self.camera.Gain

