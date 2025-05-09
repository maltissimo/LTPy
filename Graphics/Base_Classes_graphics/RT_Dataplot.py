import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy


class RealTime_plotter(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.plotWidget = pg.PlotWidget()
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
        self.plotWidget.showGrid(x=True, y=True, alpha = 0.75)

        self.xData = []
        self.yData = []

        self.plotWidget.enableAutoRange('xy')

        self.customLabel = pg.TextItem("Custom Label", color = 'black', anchor = (0,1))
        self.plotWidget.addItem(self.customLabel)
        self.plotWidget.getViewBox().sigRangeChanged.connect(self.updateLabelPosition)

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

    def updateLabelPosition(self):
        viewRange = self.plotWidget.getViewBox().viewRange()
        x_min, x_max = viewRange[0]
        y_min, y_max = viewRange[1]

        self.customLabel.setPos(x_min + 0.1*(x_max - x_min), y_min + 0.1*(y_max - y_min))

    def setCustomLabel(self, text):
        """
        Update the label
        :param text: text for the update.
        :return:
        """
        self.customLabel.setText(text)

    def writeLabel(self, type = None, value = None, units = None):
        """
        writing a custom label for the graph. Example:
        self.warning.writelabel(type = "RMS slope", value = "1.44", unit = "urad")

        :param type: RMS slope or height, for example
        :param value: value of the RMS calculations, for example
        :param units: units needed for the label, i.e. urad for the slope.
        :return:
        """
        mylabel =  str(type) +  " : " + str(value) + "[" + str (units) + "]"
        return mylabel

    def stopTimer(self):
        self.timer.stop()

    def clearPlot(self):
        self.xData = []
        self.yData = []
        self.plotData.setData([], [])



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWin = QtWidgets.QMainWindow()
    plotterWidget = RealTime_plotter()

    # Set the plotter widget as the central widget of the main window
    mainWin.setCentralWidget(plotterWidget)
    mainWin.show()

    sys.exit(app.exec_())
