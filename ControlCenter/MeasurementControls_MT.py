import datetime
from itertools import filterfalse

from ControlCenter import Control_Utilities as cu
from ControlCenter.Laser_MT import *
from ControlCenter.Measurement import *
from ControlCenter.MotorControls_MT import *
from Graphics.Base_Classes_graphics.Measurements_GUI import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from Graphics.Base_Classes_graphics.RT_Dataplot import *
from Graphics.CameraViewer_MT import *

LENSFOCAL = 500  # this is the nominal focal length in mm of our lens
ZERO_X = 5280 / 2  # Have to start somewhere, this is half of camera.Width()
ZERO_Y = 4600 / 2  # Have to start somewhere, this is half of camera.Height()

TODAY = datetime.datetime.now().strftime("%H-%M-%S_%Y%m%d")


class MeasurementControls(QMainWindow):
    f = LENSFOCAL  # this is now in mm
    X0 = ZERO_X
    Y0 = ZERO_Y

    def __init__(self, PMAC_credentials): #, motor_timer : QTimer, camera_timer : QTimer):
        if not PMAC_credentials:
            connector = cu.Connection_initer()
            PMAC_credentials = connector.get_credentials()
        print("inside MeasurementControls: ")
        print(PMAC_credentials["ip"])
        print(PMAC_credentials["username"])
        print(PMAC_credentials["password"])

        self.pmac_ip = PMAC_credentials["ip"]
        # print(self.pmac_ip)
        self.pmac_username = PMAC_credentials["username"]
        # print(self.pmac_username)
        self.pmac_password = PMAC_credentials["password"]
        # print(self.pmac_password)

        # Initing objects for the measurements:
        self.motor_timer = QTimer()
        self.camera_timer = QTimer()

        self.motors = MotorControls(PMAC_credentials)
        #self.camera = Camera() commented out as this is called by CamViewer in the initCameraTab method
        self.laser = Laser()
        self.measurement = Measurement()

        # Some sanity values:

        self.length = 0.0  # this is the length (in mm ) of the measurement
        self.points = 0  # these are the number of measurement points
        self.stepsize = 0.0  # this is the stepsize ( in mm) of the measurement
        self.nrofgrabs = 5  # default nr of camera grabs per measurement point
        self.xStartPos = self.motors.X.get_real_pos()

        # Create an instance of the Measurement_GUI class:
        super().__init__()

        self.gui = Ui_MeasurementGUI()
        self.gui.setupUi(self)


        # Dealing with the GUI:

        self.initHeightTab()
        self.initSlopesTab()
        self.initCameraTab()

        print("Nr of measurement points: ", self.points)
        print("Measurement lenght: ", self.length)
        print("Measurement stepsize: ", self.stepsize)

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
        my_mm_length = float(self.gui.length_input.text())
        self.length = cu.MathUtils.mm2um(my_mm_length)
        self.gui.length_input.clear()

    def get_stepsize(self):
        self.stepsize = float(self.gui.stepsize_input.text())
        self.stepsize = cu.MathUtils.mm2um(self.stepsize)
        self.gui.stepsize_input.clear()

    def get_nrofgrabs(self):
        self.nrofgrabs = int(self.gui.nrofgrabs_input.text())
        self.gui.nrofgrabs_input.clear()

    def conditions_check(self):
        # Check if laser is on:

        if self.laser.is_on != 'ON':
            self.show_warning(title = "Laser Warning!", message = "Laser is currently off, cannot start measurement")
            return False

        if self.points != 0 and self.stepsize != 0.0 and self.length == 0.0:
            self.length = self.points * self.stepsize
            print("Nr of measurement points: ", self.points)
            print("Measurement lenght: ", self.length)
            print("Measurement stepsize: ", self.stepsize)
            return True
            # this is um, as the values are set in micron straight after user input

        elif self.stepsize != 0.0 and self.length != 0.0 and self.points == 0:
            self.points = int(self.length / self.stepsize)
            print("Nr of measurement points: ", self.points)
            print("Measurement lenght: ", self.length)
            print("Measurement stepsize: ", self.stepsize)
            return True

        elif self.length != 0.0 and self.points != 0 and self.stepsize == 0.0:
            self.stepsize = self.length / self.points
            print("Nr of measurement points: ", self.points)
            print("Measurement lenght: ", self.length)
            print("Measurement stepsize: ", self.stepsize)
            return True

        else:
            self.show_warning(title = "Missing Values!",
                              message = "At least two between Length, Step Size and Number of points are required")
        return False

    def setXstartPos(self):
        self.warning.show_warning(title = "Setting measurement start position!", message = "Set the X stage at the desired starting position!")
        self.xStartPos = self.motors.X.get_real_pos()
        print(" X start position: ", self.xStartPos)

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

    def writeheader(self):
        header = ""
        header += "date of measurement: " + TODAY + "\n"
        header += "Nr of camera grabs per point: " + str(self.nrofgrabs) + "\n"
        header += "Length of measurement (mm): " + str(self.length) +"\n"
        header += "Nr of measurement points: " +  str(self.points) + "\n"
        header += "Stepsize of measurement: " + str(self.stepsize) + "\n"
        header += "\t" + "X" + "\t\t" + "Y" + "\t\t" + "Centroid" + "\n"
        header += "\n"
        return header


    def startMeasurement(self):

        self.slopes_plot.clearPlot() # Clear plot at the beginning of the measurement.

        self.camViewer.camera.set_grab_nr(1)

        if not self.conditions_check():
            return

        self.results = self.writeheader()
        print(self.results)
        #Instantiating the arrays for storing the results
        myposarray = np.array([])
        mystepposarray = np.array([])
        slopesarray = np.array([])
        heightsarray = np.array([])

        if self.motors.X.get_real_pos()- self.xStartPos > 1.0: # difference bigger than 1 micron
            self.show_warning("Head moving", "Moving X Stage to starting position")
            self.motors.xmove.move_abs(speed = "rapid", coord = self.xStartPos)

        # This below is the main measurement loop
        for i in range(self.points):
            mypos = self.motors.X.get_real_pos()  # this is in microns
            mysteppos = i * self.stepsize # this is in microns, a lot better for graphical representation.
            print("\n")
            print("Moved to position ", i + 1, f" of {self.points}")
            print("X coord: ", mypos, "\n")

            averageX= 0.0  # resetting back to 0 after each round of the loop below.
            averageY = 0.0

            for grab in range(self.nrofgrabs):
                image = self.camViewer.camera.acquire_once()
                self.camViewer.camera.frame = image
                #print(type(image))
                centroid = self.measurement.centroid(image)
                averageX += centroid[1]
                #print("Current meas centroid X: ", centroid[0])
                averageY += centroid[0]
                #print("Current meas centroid Y: ", centroid[1])
                grab += 1

            averageCentroidX = averageX / self.nrofgrabs
            averageCentroidY = averageY / self.nrofgrabs
            #print("Current averaged centroid Y: ", averageCentroidY, "\n")

            slope = self.measurement.slope_calc(averageCentroidY)

            slopesarray = np.append(slopesarray, slope)
            #print(slopesarray)

            self.results += (str(mypos) + "\t" + str(self.motors.Y.get_real_pos()) +
                             "\t" + str(averageCentroidX) + "\t" + str(averageCentroidY) + "\n")

            myposarray = np.append(myposarray, mypos - self.xStartPos)

            mystepposarray = np.append(mystepposarray, mysteppos)

            #self.height_plot.updatePlot(mystepposarray[-1] * 1000, heightsarray[-1])
            #self.slopes_plot.updatePlot(mystepposarray[-1] / 1000, slopesarray[-1])
            #print(self.motors.X.get_real_pos())
            self.motors.xmove.move_rel(speed = "rapid", distance= self.stepsize)
            i += 1

        # Calculating heights:

        fit = self.measurement.my_fit(arrayX = myposarray, arrayY = slopesarray, order = 1)
        to_be_plotted = slopesarray - fit # this is the REAL measurement value
       # print(type(to_be_plotted))

        heightsarray = self.measurement.height_calc(to_be_plotted, myposarray)

        for i in range(len(heightsarray)):
            self.slopes_plot.updatePlot(mystepposarray[i] / 1000, to_be_plotted[i])
            self.height_plot.updatePlot(mystepposarray[i] / 1000, heightsarray[i])
        #Calculating rms, then updating plots

        self.measurement.slopes_rms = self.measurement.RMS(to_be_plotted)
        print(self.measurement.slopes_rms)
        self.measurement.heights_rms = self.measurement.RMS(heightsarray)
        roundslope = round(1000000 * self.measurement.slopes_rms, 3)
        roundheight = round(self.measurement.heights_rms, 3)
        slopelabel = self.slopes_plot.writeLabel(type = "RMS Slopes", value = roundslope , units = "urad")
        heightlabel = self.height_plot.writeLabel(type = "RMS Heights",value = roundheight, units = "um")

        self.slopes_plot.setCustomLabel(slopelabel)
        self.height_plot.setCustomLabel(heightlabel)

        self.save_data(myposarray, slopesarray, heightsarray)

        self.endmeasurement()

    def save_data(self, myposarray, slopesarray, heightsarray):

        if self.gui.savelldata.isChecked():
            filename = "FullData" + TODAY + ".txt"
            self.measurement.save_data(filename, self.results)
            #self.show_warning( "Full Data saved", f"Data saved into {filename}")

        slopestobesaved = "Slope RMS: " + str(self.measurement.slopes_rms) + "\n"
        heightstobesaved = "Height RMS: " + str(self.measurement.heights_rms) + "\n"
        slopestobesaved += self.measurement.pretty_printing(myposarray, slopesarray)
        heightstobesaved += self.measurement.pretty_printing(myposarray, heightsarray)

        filename2 = "Xpos_slopes" + TODAY + ".txt"
        filename3 = "Xpos_heights" + TODAY + ".txt"

        self.measurement.save_data(filename2, slopestobesaved)
        self.measurement.save_data(filename3, heightstobesaved)
        if self.gui.savelldata.isChecked():
            self.show_warning("Data saved!", f"Data saved into {filename}, {filename2}, {filename3}")

        else:
            self.show_warning("Data saved!", f"Data saved into {filename2}, {filename3}")

    def endmeasurement(self):
        """Housekeeping after each single measurement"""
        self.motors.restartTimer()
        self.camViewer.camera.set_grab_nr(5)
        self.camViewer.start_grab()
        """ self.points = 0
        self.nrograbs = 5
        self.setpsize = 0.0
        self.length = 0.0"""
        self.motors.xmove.move_abs(speed = "rapid", coord = float(self.xStartPos))
        self.show_warning("End of Measurement!", "Stage at the original position.")

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
        self.show_warning("Warning!", "Measurement starting position set!")

    def initHeightTab(self):
        self.height_plot = RealTime_plotter()

        self.height_plot.setLabels(bottom_label = "X position", bottom_units = "mm", left_label="Heights", left_units = "um")

        height_layout = QtWidgets.QVBoxLayout()
        height_layout.addWidget(self.height_plot)

        self.gui.height_tab.setLayout(height_layout)

    def initSlopesTab(self):
        self.slopes_plot = RealTime_plotter()
        self.slopes_plot.setLabels(bottom_label = "X position", bottom_units = "mm", left_label="Slope", left_units = "rad")

        slopes_layout = QtWidgets.QVBoxLayout()
        slopes_layout.addWidget(self.slopes_plot)

        self.gui.Slopes_tab.setLayout(slopes_layout)

    def initCameraTab(self):

        self.camViewer = CamViewer()

        CamTabLayout = QtWidgets.QVBoxLayout(self.gui.cam_tab)
        CamTabLayout.addWidget(self.camViewer)

        self.gui.cam_tab.setLayout(CamTabLayout)

    def show_warning(self, title, message):
        warning = myWarningBox(
            title=title,
            message=message,
            parent=self
        )
        warning.show_warning()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MeasurementControls(None)
    window.show()
    sys.exit(app.exec_())
