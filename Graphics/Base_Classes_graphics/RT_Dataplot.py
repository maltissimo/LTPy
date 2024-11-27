import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class RealTime_plotter(QWidget):
    def __init__(self, custom_timer : QTimer, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)
        self.layout.addWidget(self.plotWidget)

        self.plotData = self.plotWidget.plot([], [],
                                             pen=pg.mkPen(color='b', width=2),
                                             symbol='d',
                                             symbolpen='b',
                                             symbolSize=8)
        mypen = pg.mkPen('k', width=2)
        self.plotWidget.setBackground('w')
        self.plotWidget.getAxis('left').setPen(mypen)
        self.plotWidget.getAxis('bottom').setPen(mypen)
        self.plotWidget.getAxis('left').setTickPen(mypen)  # Set left axis ticks color to black
        self.plotWidget.getAxis('bottom').setTickPen(mypen)
        self.plotWidget.getAxis('left').setTextPen(mypen)
        self.plotWidget.getAxis('bottom').setTextPen(mypen)

        self.xData = []
        self.yData = []

        self.timer = custom_timer
        #self.timer.start(100)
        # in debugging :self.timer.timeout.connect(self.dummyUpdatePlot)
        self.timer.timeout.connect(self.updatePlot)

    def updatePlot(self, dataX, dataY):
        """
        this is the real deal. Must be connected to Gantry Motor(X) and the math from the camera.
        :return:
        """

        self.xData.append(dataX)
        self.yData.append(dataY)

        self.plotData.setData(self.xData, self.yData)

    def dummyUpdatePlot(self):
        """ this is for testing only
        import random
        newX = random.uniform(0, 100)
        newY = random.uniform(0, 100)
        self.xData.append(newX)
        self.yData.append(newY)

        self.plotData.setData(self.xData, self.yData)
        """

    def setLabels(self, bottom_label, bottom_units, left_label, left_units):
        """
        updates the axis labels according to the caller. Remember:
        x label, x units,
        y label, y units.
        :return:
        """
        self.plotWidget.setLabel("left", left_label, left_units, color='k',
                                 **{'font-size': '14pt', 'font-weight': 'bold'})
        self.plotWidget.setLabel("bottom", bottom_label, bottom_units, color='k',
                                 **{'font-size': '14pt', 'font-weight': 'bold'})

    def stopTimer(self):
        self.timer.stop()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWin = QtWidgets.QMainWindow()
    plotterWidget = RealTime_plotter()

    # Set the plotter widget as the central widget of the main window
    mainWin.setCentralWidget(plotterWidget)
    mainWin.show()

    sys.exit(app.exec_())
