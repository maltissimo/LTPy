import datetime

from ControlCenter import Control_Utilities as cu
from ControlCenter.Laser import *
from ControlCenter.Measurement import *
from ControlCenter.MotorControls import *
from Graphics.Base_Classes_graphics.Measurements_GUI import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from Graphics.Base_Classes_graphics.RT_Dataplot import *
from Graphics.CameraViewer import *

LENSFOCAL = 500  # this is the nominal focal length in mm of our lens
ZERO_X = 5280 / 2  # Have to start somewhere, this is half of camera.Width()
ZERO_Y = 4600 / 2  # Have to start somewhere, this is half of camera.Height()

TODAY = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


class MeasurementControls(QMainWindow):
    f = LENSFOCAL  # this is now in mm
    X0 = ZERO_X
    Y0 = ZERO_Y

    def __init__(self, PMAC_credentials):
        if not PMAC_credentials:
            connector = cu.Connection_initer()
            PMAC_credentials = connector.get_credentials()

        self.pmac_ip = PMAC_credentials["ip"]
        # print(self.pmac_ip)
        self.pmac_username = PMAC_credentials["username"]
        # print(self.pmac_username)
        self.pmac_password = PMAC_credentials["password"]
        # print(self.pmac_password)

        # Initing objects for the measurements:

        self.motors = MotorControls(PMAC_credentials)
        #self.camera = Camera() commented out as this is called by CamViewer in the initCameraTab method
        self.laser = Laser()
        self.measurement = Measurement()

        # Some sanity values:

        self.length = 0  # this is the length (in mm ) of the measurement
        self.points = 0  # these are the number of measurement points
        self.stepsize = 0  # this is the stepsize ( in mm) of the measurement
        self.nrofgrabs = 5  # default nr of camera grabs per measurement point

        # Create an instance of the Measurement_GUI class:
        super().__init__()

        self.gui = Ui_MeasurementGUI()
        self.gui.setupUi(self)

        # Dealing with the GUI:

        self.initHeightTab()
        self.initSlopesTab()
        self.initCameraTab()

        self.gui.points_input.returnPressed.connect(self.get_points)
        self.gui.length_input.returnPressed.connect(self.get_length)
        self.gui.stepsize_input.returnPressed.connect(self.get_stepsize)
        self.gui.nrofgrabs_input.returnPressed.connect(self.get_nrofgrabs)

        self.gui.startButton.clicked.connect(self.startMeasurement)
        self.gui.stopButton.clicked.connect(self.stopMeasurement)
        self.gui.xStartPos.clicked.connect(self.setXstartPos)

    def get_points(self):
        self.points = int(self.gui.points_input.text())
        self.gui.points_input.clear()

    def get_length(self):
        self.length = float(self.gui.length_input.text())
        self.length = cu.MathUtils.mm2um(self.length)
        self.gui.length_input.clear()

    def get_stepsize(self):
        self.stepsize = float(self.gui.stepsize_input.text())
        self.stepsize = cu.MathUtils.mm2um(self.stepsize)
        self.gui.stepsize_input.clear()

    def get_nrofgrabs(self):
        self.nrofgrabs = int(self.gui.nrofgrabs_input.text())
        self.gui.nrofgrabs_input.clear()

    def conditions_check(self):

        if self.points != 0 and self.stepsize != 0 and self.length == 0:
            self.length = self.points * self.stepsize  # this is um, as the values are set in micron straight after user input

        elif self.stepsize != 0 and self.length != 0 and self.points == 0:
            self.points = self.length / self.stepsize

        elif self.length != 0 and self.points != 0 and self.stepsize == 0:
            self.stepsize = self.length / self.points

        else:
            self.show_warning("Missing Values!",
                              "At least two between Length, Step Size and Number of points are required")

    def setXstarPos(self):
        self.show_warning("Setting measurement start position!", "Set the X stage at the desired starting position!")
        self.xStartPos = self.motors.X.get_real_pos()

    def show_warning(self, title, message):
        warning = myWarningBox(
            title=title,
            message=message,
            parent=self
        )
        warning.show_warning()

    def get_all_motor_pos(self):
        """
        This spits out a formatted text. I think it's better creating a method rather than using inside the measure for cycle.
        :return: all_motor_pos.
        """
        pos_all = ""
        pos_all += str(self.xmotor.get_real_pos) + "\t"
        pos_all += str(self.ymotor.get_real_pos) + "\t"
        pos_all += str(self.zmotor.get_real_pos) + "\t"
        pos_all += str(self.pitch.get_real_pos) + "\t"
        pos_all += str(self.roll.get_real_pos) + "\t"
        pos_all += str(self.yaw.get_real_pos) + + "\t"
        return (pos_all)

    def startMeasurement(self):

        self.motors.stopTimer()  # stops the positions from updating, to free band
        self.height_plot.stopTimer()  # stops the automatic plot update, no need for it.
        self.slopes_plot.stopTimer()
        self.camera.setgrab_nr(1)
        if gui.savealldata.isChecked():
            self.results = ""
            self.results += "date of measurement: " + TODAY + "\n"
            self.results += "Nr of camera grabs per point: " + str(self.nrofgrabs) + "\n"
            self.results += "\t" + "X" + "\t" + "Y" + "\t" + "Centroid" + "\n"
            self.results += "\n"
        myposarray = []
        slopesarray = []
        heightsarray = []

        if self.motors.x.get_real_pos() != self.xStartPos:
            self.motors.xmove(self.xStartPos)

        # This below is the main measurement loop
        for i in range(self.points):
            mypos = self.motors.X.get_real_pos()  # this is in microns

            averageX, averageY = 0.0  # resetting back to 0 after each round of the loop below.

            for grab in range(self.nrofgrabs):
                image = self.camera.grabdata()
                centroid = self.measurement.centroid(image)
                averageX += centroid[0]
                averageY += centroid[1]
                grab += 1

            averageCentroidX = averageX / self.nrofgrabs
            averageCentroidY = averageY / self.nrofgrabs

            slope = self.measurement.slope_calc(averageCentroidY, Y0, f)
            height = self.measurement.height_calc()
            self.results += str(mypos) + "\t" + str(self.motors.Y.get_real_pos()) + "\t" + str(
                averageCentroidX) + "\t" + str(averageCentroidY) + "\n"

            myposarray.append(mypos)
            slopesarray.append(slope)
            heightsarray.append(height)
            self.height_plot.updatePlot(mypos * 1000, height)
            self.slopes_plot.updatePlot(mypos * 1000, slope)
            self.motors.xmove.move_rel(self.stepsize)
            i += 1

        # Housekeeping, data saving:

        myposarray = np.array(myposarray)
        slopesarray = np.array(slopesarray)
        heightsarray = np.array(heightsarray)
        if gui.savealldata.isChecked():
            filename = "FullData" + TODAY + ".txt"
            self.measurement.save_data(filename, results)
            self.show_warning("Full Data saved", f"Data saved into {filename}")

        slopestobesaved = self.measurement.pretty_printing(myposarray, slopesarray)
        heightstobesaved = self.measurement.pretty_printing(myposarray, heightsarray)

        filename2 = "Xpos_slopes" + TODAY + ".txt"
        filename3 = "Xpos_heights" + TODAY + ".txt"

        self.measurement.save_data(filename2, slopestobesaved)
        self.measurement.save_data(filename3, heightstobesaved)
        self.show_warning("Slopes and heights saved!", f"Data saved into {filename2}, {filename3}")

        self.motors.restartTimer()
        self.camera.set_grab_nr(5)

    def stopMeasurement(self):
        # TODO: dump all the motors positions into a file. Then set the positions after homing to those values
        self.motors.stopall()
        self.motors.restartTimer()
        self.camera.set_grab_nr(5)
        autopos = self.motors.X.get_real_pos
        self.show_warning("Warning!", "Measurement interrupted")
        self.motors.MotorUtil.homeGantry()
        self.motors.xmove.moveabs(autopos)

    def setXstartPos(self):
        self.xStartPos = self.motors.X.get_real_pos()

    def initHeightTab(self):
        self.height_plot = RealTime_plotter()

        self.height_plot.setLabels("X position", "mm", "Heights", "µm")

        height_layout = QtWidgets.QVBoxLayout()
        height_layout.addWidget(self.height_plot)

        self.gui.height_tab.setLayout(height_layout)

    def initSlopesTab(self):
        self.slopes_plot = RealTime_plotter()
        self.slopes_plot.setLabels("X position", "mm", "Slopes", "µrad")

        slopes_layout = QtWidgets.QVBoxLayout()
        slopes_layout.addWidget(self.slopes_plot)

        self.gui.Slopes_tab.setLayout(slopes_layout)

    def initCameraTab(self):

        self.camViewer = CamViewer()

        CamTabLayout = QtWidgets.QVBoxLayout(self.gui.cam_tab)
        CamTabLayout.addWidget(self.camViewer)

        self.gui.cam_tab.setLayout(CamTabLayout)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MeasurementControls(None)
    window.show()
    sys.exit(app.exec_())
