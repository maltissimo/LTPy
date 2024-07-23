from Hardware.Motors import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys

class CoordReader(QtGui.QTextFrame):
    def __init__(self, Gantry, motors = [X,Y,Z, pitch, roll, yaw],
                 parent = None, on_top = False
                 ):
        QtGui.QTextFrame.__init__(self, parent)

        if on_top:
            self.setWindowFlags(QtCore.Qt.WindowsStaysOnTopHint)

        self.Gantry = Gantry
        self.motors = motors
        self.update_rate = 1
        self.widgets = widgets = []

        layout = QtGui.QFormLayout()
        for motor in motors:
            widgets.append(QtGui.QLabel('0,0'))
            label = widgets[-1]
            label.setAlignment(Qt.AlignRight)
            layout.addRow(str(motor), label)

        self.setLayout(layout)

        QTimer.singleShot(0, self.update) # the 0 is in msecs.

    def update(self):
        t0 = time.time()

        motors = self.motors()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CoordinateReader()
    sys.exit(app.exec_())