from PyQt5.QtWidgets import QMainWindow

from Graphics.Base_Classes_graphics.Align_helper_GUI import *
from Graphics.Base_Classes_graphics.RT_Dataplot import *


class Align_helper(QMainWindow):
    def __init__(self, parent=None):
        super().__init(parent)

        self.setWindowTitle("Alignment Helper window")

        self.ui = Ui_DockWidget()
        self.gui.setupUi(self)

        self.centroidX_plotter = RealTime_plotter(self.ui.centroidX)
        self.centroidY_plotter = RealTime_plotter(self.ui.centroidY)
        self.slopes_plotter = RealTime_plotter(self.ui.slopes)
        self.height_plotter = RealTime_plotter(self.ui.heights)

        self.resize(1024, 768)

    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        window = MotorControls()
        window.show()
        sys.exit(app.exec_())
