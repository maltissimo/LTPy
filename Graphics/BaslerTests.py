from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMainWindow,QVBoxLayout
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
import pypylon.pylon as py
class Detector():
    def __init__(self):
        self.camera = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.StartGrabbing(py.GrabStrategy_LatestImageOnly)
        self.frame = None

    def grab_frame(self):
        """if self.camera.isGrabbing():"""
        res = self.camera.RetrieveResult(5000, py.TimeoutHandling_ThrowException)
        if res.GrabSucceeded():
            self.frame = res.Array
        res.Release()


class Viewer():
    def __init__(self, detector):
        self.detector = detector
        plt.ion()
        self.fig, self.ax = plt.subplots()

    def plot_frame(self):
        if self.detector.camera.IsGrabbing:
            self.ax.clear()
            self.ax.imshow(self.detector.frame)
            plt.draw()
            plt.pause(0.001)

