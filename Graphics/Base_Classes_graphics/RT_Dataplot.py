import pyqtgraph as pg
from ControlCenter import Timing
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class RealTime_plotter(QWidget):
    def __init__(self, parent = None):
        super(RealTime_plotter, self).__init(parent)
        self.layout = QVBoxLayout
        self.setLayout(self.layout)


        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)

        self.plotData = self.plotWidget.plot([],[], pen = pg.mkPend(color = 'b', width = 2))

        self.xData = []
        self.yData =[]

        self.timer = Timing.myTimer(interval= 50) # set the interval here.

        self.timer.connect_callback(self.updatePlot)
        self.timer.start() # timeout is every 50 ms, see line 21

    def updatePlot(self):
        """
        this is the real deal. Must be connected to Gantry Motor(X) and the math from the camera.
        :return:


        newX = motorpos(X)
        newY = height(fromCamera)

        self.xData.append(newX)
        self.yData.append(newY)

        self.plotData.setData(self.xData, self.yData)"""

    def dummyUpdatePlot(self):

        """ this is for testing only"""
        import random
        newX = random.uniform(0,100)
        newY = random.uniform(0, 100)
        self.xData.append(newX)
        self.yData.append(newY)

        self.plotData.setdata(self.xData, self.yData)
