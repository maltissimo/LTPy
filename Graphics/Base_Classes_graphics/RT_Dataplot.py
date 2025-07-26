import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

class MyPlot:
    def __init__(self, color = 'b', width = 1,
                 symbol = "d", symbolSize = 8, symbolBrush = None, symbolPen = None,
                 name = "plot", y_axis  = "left"):
        self.xData = []
        self.yData = []
        self.color = color
        self.width = width
        self.symbol = symbol
        self.symbolSize = symbolSize
        if symbolBrush is None:
            self.symbolBrush = color
        else:
            self.symbolBrush = symbolBrush
        if symbolPen is None:
            self.symbolPen = color
        else:
            self.symbolPen = symbolPen

        self.name = name
        self.y_axis = y_axis # This sets the Y axis  left of right.
        self.plotItem = None
        self.pen = pg.mkPen(color = color, width = width)

    def addData(self, x, y):
        self.xData.append(x)
        self.yData.append(y)

    def addDataBreak(self):
        """Adds a break in the data to avoid unwanted plotting connections"""
        self.xData.append('nan')
        self.yData.append('nan')

    def replaceAllData(self, x_array, y_array):
        """Replace all data at once, to avoid unwanted plotting connections"""
        self.xData= list(x_array)
        self.yData = list(y_array)
        if self.plotItem is not None:
            self.plotItem.setData(self.xData, self.yData)

    """def setData(self, x_array, y_array):
        self.xData = x_array
        self.yData = y_array"""

    def clearData(self):
        self.xData = []
        self.yData = []
        if self.plotItem is not None:
            self.plotItem.setData([],[])

    def clearPlot(self):
        self.clearData()
        self.updatePlotItem()

    def updatePlotItem(self):
        if self.plotItem is not None:
            self.plotItem.setData(self.xData, self.yData, connect = "all")

class RealTime_plotter(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)

        self.rightViewBox = pg.ViewBox()
        self.plotWidget.plotItem.scene().addItem(self.rightViewBox)
        #self.plotWidget.addItem(self.rightViewBox)
        self.plotWidget.plotItem.getAxis('right').linkToView(self.rightViewBox)
        self.rightViewBox.setXLink(self.plotWidget.plotItem)

        self.plotWidget.plotItem.showAxis("right")

        self.plots_left = [] # a list to store all the incoming plots
        self.plots_right = []

        mypen = pg.mkPen('k', width=2)
        self.plotWidget.setBackground('w')

        #Left Axis:
        self.plotWidget.getAxis('left').setPen(mypen)
        self.plotWidget.getAxis('bottom').setPen(mypen)
        self.plotWidget.getAxis('left').setTickPen(mypen)  # Set left axis ticks color to black
        self.plotWidget.getAxis('bottom').setTickPen(mypen)
        self.plotWidget.getAxis('left').setTextPen(mypen)
        self.plotWidget.getAxis('bottom').setTextPen(mypen)

        #Right Axis:
        self.plotWidget.getAxis('right').setPen(mypen)
        self.plotWidget.getAxis('right').setTickPen(mypen)
        self.plotWidget.getAxis('right').setTextPen(mypen)

        #self.plotWidget.showGrid(x=True, y=True, alpha = 0.75)
        self.plotWidget.enableAutoRange('xy')
        self.rightViewBox.enableAutoRange('xy')

        self.customLabel = pg.TextItem(text = "", color = 'black', anchor = (0,1))
        self.plotWidget.addItem(self.customLabel)

        self.plotWidget.getViewBox().sigRangeChanged.connect(self.updateLabelPosition)
        self.plotWidget.getViewBox().sigRangeChanged.connect(self.updateRightViewBox)
        self.plotWidget.getViewBox().sigResized.connect(self.updateRightViewBox)

        #print("RealTime_plotter initialized")

    def updateRightViewBox(self):
        self.rightViewBox.setGeometry(self.plotWidget.getViewBox().sceneBoundingRect())
        self.rightViewBox.linkedViewChanged(self.plotWidget.getViewBox(), self.rightViewBox.XAxis)
        self.rightViewBox.linkedViewChanged(self.plotWidget.getViewBox(), self.rightViewBox.XAxis)

    """def calculateauAutoRange(self, plots_list):
        if not plots_list:
            return None, None
        all_y_data = []
        for plot in plots_list:
            if plot.yData:
                all_y_data.extend(plot.yData)
        if not all_y_data:
            return None, None

        min_val = min(all_y_data)
        max_val = max(all_y_data)
        y_range = max_val - min_val
        if range == 0:
            y_range = abs(max_val) *0.1 if max_val != 0 else 1
        padding = y_range * 0.1

        return min_val - padding, max_val + padding
    def updateAutoRanges(self):
        if self.plots_left:
            y_min, y_max = self.calculateauAutoRange(self.plots_left)
            if y_min is not None and y_max is not None:
                self.plotWidget.setYRange(y_min, y_max, padding = 0)

        if self.plots_right:
            y_min, y_max = self.calculateauAutoRange(self.plots_right)
            if y_min is not None and y_max is not None:
                self.rightViewBox.setYRange(y_min, y_max, padding = 0)"""

    def forceAutoRange(self):
        self.plotWidget.autoRange()
        self.rightViewBox.autoRange()

    def addPlot(self, myplot):
        if myplot.y_axis == "right":
            plot_item = pg.PlotCurveItem(pen=pg.mkPen(color=myplot.color, width=myplot.width),
                                             symbol=myplot.symbol,
                                             symbolSize=myplot.symbolSize,
                                             symbolBrush=myplot.symbolBrush,
                                             symbolPen=myplot.symbolPen,
                                             name = myplot.name)
            self.rightViewBox.addItem(plot_item)
            self.plots_right.append(myplot)
        else:
            plot_item = self.plotWidget.plot([], [],
                                             pen = pg.mkPen(color = myplot.color, width = myplot.width),
                                             symbol = myplot.symbol,
                                             symbolSize = myplot.symbolSize,
                                             symbolBrush = myplot.symbolBrush,
                                             symbolPen = myplot.symbolPen,
                                             name = myplot.name
                                             )
            self.plots_left.append(myplot)

        myplot.plotItem = plot_item
        return myplot

    def removePlot(self, myplot):
        if myplot in self.plots_left:
            if myplot.plotItem is not None:
                self.plotWidget.removeItem(myplot.plotItem)
                myplot.plotItem = None
            self.plots_left.remove(myplot)
        elif myplot in self.plots_right:
            if myplot.plotItem is not None:
                self.rightViewBox.removeItem(myplot.plotItem)
                myplot.plotItem = None
            self.plots_right.remove(myplot)

    def updatePlotBatch(self, plot, x_array, y_array):
        if plot in self.plots_left or plot in self.plots_right:
            plot.replaceAllData(x_array, y_array)

    def updatePlot(self, myplot,dataX, dataY):
        """
        this is the real deal.
        """
        if myplot in self.plots_left or myplot in self.plots_right:
            myplot.addData(dataX, dataY)
            myplot.updatePlotItem()
        """if myplot in self.plots_right:
            self.rightViewBox.enableAutoRange(axis = "xy")
        if myplot in self.plots_right:
            self.rightViewBox.autoRange()
        else:
            self.plotWidget.autoRange()

        #self.plotData.setData(self.xData, self.yData)"""

    def dummyUpdatePlot(self):
        """ this is for testing only
        import random
        newX = random.uniform(0, 100)
        newY = random.uniform(0, 100)
        self.xData.append(newX)
        self.yData.append(newY)

        self.plotData.setData(self.xData, self.yData)
        """

    def setLabels(self, bottom_label, bottom_units,
                  left_label, left_units,
                  right_label = None, right_units = None):
        """
        updates the axis labels according to the caller. Remember:
        x label, x units,
        y label, y units.
        :return:
        """
        self.plotWidget.setLabel("left", left_label, left_units, color='k',
                                 **{'font-size': '12pt', 'font-weight': 'bold'})
        self.plotWidget.setLabel("bottom", bottom_label, bottom_units, color='k',
                                 **{'font-size': '12pt', 'font-weight': 'bold'})
        if right_label:
            self.plotWidget.setLabel("right", right_label, right_units, color='k',
                                     **{'font-size': '12pt', 'font-weight': 'bold'})

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


    def clearAllPlots(self):
        for plot in self.plots_left + self.plots_right:
            plot.clearData()
            #plot.updatePlotItem()
        self.forceAutoRange()


    def clearPlot(self):
        if len(self.plots_left) >0 or len(self.plots_right) > 0:
            for plot in self.plots_left + self.plots_right:
                plot.clearData()
                plot.updatePlotItem()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWin = QtWidgets.QMainWindow()
    plotterWidget = RealTime_plotter()

    # Set the plotter widget as the central widget of the main window
    mainWin.setCentralWidget(plotterWidget)
    mainWin.show()

    sys.exit(app.exec_())
