import sys

from PyQt5.QtWidgets import QMainWindow

from combotest import *


class test(QMainWindow):

    def __init__(self):
        super().__init__()

        self.gui = Ui_MainWindow()
        self.gui.setupUi(self)

        self.movesdict = {"X": "xmove",
                          "Y": "ymove",
                          "Z": "zmove",
                          "pitch": "pitchmove",
                          "roll": "rollmove",
                          "yaw": "yawmove"
                          }

        self.gui.comboBox.addItems(self.movesdict.keys())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = test()
    window.show()
    sys.exit(app.exec_())
