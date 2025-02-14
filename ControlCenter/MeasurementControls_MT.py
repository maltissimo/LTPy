import datetime
from itertools import filterfalse

from ControlCenter import Control_Utilities as cu
from ControlCenter.Control_Utilities import MathUtils
from ControlCenter.Laser_MT import *
from ControlCenter.Measurement import *
from ControlCenter.MotorControls_MT import *
from Graphics.Base_Classes_graphics.Measurements_GUI import *
from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox
from Graphics.Base_Classes_graphics.RT_Dataplot import *
from Graphics.CameraViewer_MT import *

LENSFOCAL = 502.5  # this is the nominal focal length in mm of our lens
ZERO_X = 5280 / 2  # Have to start somewhere, this is half of camera.Width()
ZERO_Y = 4600 / 2  # Have to start somewhere, this is half of camera.Height()

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
        self.today = datetime.datetime.now().strftime("%H-%M_%Y%m%d")

        # Create an instance of the Measurement_GUI class:
        super().__init__()

        self.gui = Ui_MeasurementGUI()
        self.gui.setupUi(self)


        # Dealing with the GUI:

        self.initHeightTab()
        self.initSlopesTab()
        self.initCameraTab()

        """print("Nr of measurement points: ", self.points)
        print("Measurement lenght: ", self.length)
        print("Measurement stepsize: ", self.stepsize)"""

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
        points_message = str(self.points)
        self.gui.points_display.setText(points_message)

    def get_length(self):
        my_mm_length = float(self.gui.length_input.text())
        self.length = cu.MathUtils.mm2um(my_mm_length)
        self.gui.length_input.clear()
        length_message = str(my_mm_length)
        self.gui.length_display.setText(length_message)

    def get_stepsize(self):
        stepsize = float(self.gui.stepsize_input.text())
        self.stepsize = cu.MathUtils.mm2um(stepsize)
        self.gui.stepsize_input.clear()
        stepsize_message = str(stepsize)
        self.gui.stepsize_display.setText(stepsize_message)

    def get_nrofgrabs(self):
        self.nrofgrabs = int(self.gui.nrofgrabs_input.text())
        self.gui.nrofgrabs_input.clear()
        grabs_message =str(self.nrofgrabs)
        self.gui.nrofgrabs_label_2.setText(grabs_message)

    def conditions_check(self):
        # Check if laser is on:
        #print(f"Checking conditions: Points={self.points}, Length={self.length}, Step Size={self.stepsize}")

        if self.laser.is_on != 'ON':
            self.show_warning(title = "Laser Warning!", message = "Laser is currently off, turning it on")
            self.laser.turnON(isLASON)
            return True

        if self.points != 0 and self.stepsize != 0.0 and self.length == 0.0:
            self.length = self.points * self.stepsize
            #self.print_attributes()

            return True
            # this is um, as the values are set in micron straight after user input

        elif self.stepsize != 0.0 and self.length != 0.0 and self.points == 0:
            self.points = int(self.length / self.stepsize)
            #self.print_attributes()
            return True

        elif self.length != 0.0 and self.points != 0 and self.stepsize == 0.0:
            self.stepsize = self.length / self.points
            #self.print_attributes()
            return True

        elif self.length!= 0 and self.points!= 0 and self.stepsize !=0:
            self.stepsize = self.length / self.points
            stepsize_message = str(MathUtils.um2mm(self.stepsize))
            self.gui.stepsize_display.setText(stepsize_message)
            #self.print_attributes()
            return True

        else:
            self.show_warning(title = "Missing Values!",
                              message = "NEIN! At least two between Length, Step Size and Number of points are required")
            return False
        #self.print_attributes()

        return True

    def print_attributes(self):
        print("Nr of measurement points: ", self.points + 1) # this is because one is measuring from position 0 up to X, so this is the number of intervals.
        print("Measurement length: ", self.length)
        print("Measurement stepsize: ", self.stepsize)

    def setXstartPos(self):

        self.xStartPos = self.motors.X.get_real_pos()
        mymessage = f"Set the measurement starting position @ {MathUtils.um2mm(self.XStartPos)}"
        self.warning.show_warning(title="Setting measurement start position!",
                                  message= mymessage)

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
        if datetime.datetime.now().strftime("%H-%M_%Y%m%d") != self.today:
            self.today = datetime.datetime.now().strftime("%H-%M_%Y%m%d")
        else:
            self.today = self.today
        header = ""
        header += "Date of measurement: " + self.today + "\n"
        header += "Nr of camera grabs per point: " + str(self.nrofgrabs) + "\n"
        header += "Length of measurement (mm): " + str(MathUtils.um2mm(self.length)) +"\n"
        header += "Nr of measurement points + 1: " +  str(self.points + 1 ) + "\n"
        header += "Stepsize of measurement (mm): " + str(MathUtils.um2mm(self.stepsize)) + "\n"
        header += "\t" + "X" + "\t\t" + "Y" + "\t\t" + "Centroid X" + "\t\t" + "Centroid Y"+ "\n"
        header += "\n"
        return header


    def startMeasurement(self):

        self.slopes_plot.clearPlot()# Clear plot at the beginning of the measurement.
        self.height_plot.clearPlot() # Clear plot at the beginning of the measurement

        self.camViewer.camera.set_grab_nr(1)
        self.camViewer.camera.set_exp_time(8)
        self.camViewer.stop_grab()

        if not self.conditions_check():
            return
        #print("Inside the StartMeasurement method: ")
        self.print_attributes()

        # Ensure points, length, and stepsize are set
        if self.points == 0 or self.length == 0.0 or self.stepsize == 0.0:
            self.show_warning("Missing Values!", "Please provide valid inputs for points, length, and stepsize.")
            return


        self.results = self.writeheader()
        #print(self.results)
        #Instantiating the arrays for storing the results
        myposarray = np.array([])
        mystepposarray = np.array([])
        slopesarray = np.array([])
        heightsarray = np.array([])

        if not self.motors.X.get_real_pos()- self.xStartPos > 1.0: # difference bigger than 1 micron
            print("Stage at starting position!")
            print("Stepsize set at: ", self.stepsize)
        else:
            self.show_warning("Head moving", "Moving X Stage to starting position")
            self.motors.xmove.move_abs(speed = "rapid", coord = self.xStartPos)

        # This below is the main measurement loop
        for i in range(self.points + 1):
            mypos = self.motors.X.get_real_pos()  # this is in microns
            mysteppos = i * self.stepsize # this is in microns, a lot better for graphical representation.
            print("\n")
            print("Position ", i + 1, f" of {self.points + 1}")
            label_message = "Measurement step: " + str(i + 1) + f" of {self.points}"
            self.gui.step_label.setText(label_message)
            print("Measuring @ X coord: ", mypos, "\n")

            averageX= 0.0  # resetting back to 0 after each round of the loop below.
            averageY = 0.0

            for grab in range(self.nrofgrabs):
                image = self.camViewer.camera.acquire_once()
                self.camViewer.camera.frame = image
                #print(type(image))
                centroid = cu.MathUtils.centroid( image)
                averageX += centroid[1] # this is the HOR vector @ Y = centroid[1], i.e. parallel to HOR axis
                #print("Current meas centroid X: ", centroid[0])
                averageY += centroid[0] # this is the VERTICAL vector @ X = centroid[0], i.e. parallel to vertical axis
                #print("Current meas centroid Y: ", centroid[1])
                grab += 1

            averageCentroidX = averageX / self.nrofgrabs
            averageCentroidY = averageY / self.nrofgrabs
            #print("Current averaged centroid X: ", averageCentroidX, "\n")
            #print("Current averaged centroid Y: ", averageCentroi1dY, "\n")

            slope = self.measurement.slope_calc(averageCentroidY) #changed for trial on 2024 12 20 MA, gave 14 urad with 100 grabs
            #slope = self.measurement.slope_calc(averageCentroidX) gave 2 urad, but radius way off.

            slopesarray = np.append(slopesarray, slope)
            #print(slopesarray)

            self.results += (str(mypos) + "\t\t" + str(self.motors.Y.get_real_pos()) +
                             "\t\t" + str(averageCentroidX) + "\t\t" + str(averageCentroidY) + "\n")

            myposarray = np.append(myposarray, mypos - self.xStartPos)

            mystepposarray = np.append(mystepposarray, mysteppos)
            nextpos = mypos + self.stepsize # all should be in microns
            if i != self.points:
                self.motors.xmove.move_rel(speed = "linear", distance = self.stepsize)
                while True:
                    if abs(nextpos - self.motors.X.get_real_pos())<0.05:
                        break
                    time.sleep(0.075)

                #self.motors.xmove.move_rel(speed = "rapid", distance= self.stepsize)
                i += 1
                averageCentroidX  = 0.0
                averageCentroidY = 0.0

        # Calculating heights:

        fit, radius = cu.MathUtils.my_fit(arrayX = myposarray, arrayY = slopesarray, order = 1)
        print("Radius as coeff[0], in m: ", radius / 1000000)
        to_be_plotted = slopesarray - fit # this is the REAL measurement value
       # print(type(to_be_plotted))

        heightsarray = self.measurement.height_calc(to_be_plotted, myposarray)

        for i in range(len(heightsarray)):
            self.slopes_plot.updatePlot(mystepposarray[i] / 1000, to_be_plotted[i])
            self.height_plot.updatePlot(mystepposarray[i] / 1000, heightsarray[i])
        #Calculating rms, then updating plots

        self.measurement.slopes_rms = cu.MathUtils.RMS(to_be_plotted)
        print(self.measurement.slopes_rms)
        self.measurement.heights_rms = cu.MathUtils.RMS(heightsarray)
        roundslope = round(1000000 * self.measurement.slopes_rms, 3)
        roundheight = round(self.measurement.heights_rms, 3)
        slopelabel = self.slopes_plot.writeLabel(type = "RMS Slopes", value = roundslope , units = "urad")
        heightlabel = self.height_plot.writeLabel(type = "RMS Heights",value = roundheight, units = "um")

        self.slopes_plot.setCustomLabel(slopelabel)
        self.height_plot.setCustomLabel(heightlabel)

        self.save_data(myposarray, slopesarray, heightsarray)



        self.endmeasurement()

    def save_data(self, myposarray, slopesarray, heightsarray):
        slopestobesaved = "Slope RMS: " + str(self.measurement.slopes_rms) + "\n"
        heightstobesaved = "Height RMS: " + str(self.measurement.heights_rms) + "\n"
        slopestobesaved += self.measurement.pretty_printing(myposarray, slopesarray)
        heightstobesaved += self.measurement.pretty_printing(myposarray, heightsarray)

        filename = "FullData" + self.today + ".txt"
        filename2 = "Xpos_slopes" + self.today + ".txt"
        filename3 = "Xpos_heights" + self.today + ".txt"


        if self.gui.save_slope_data.isChecked():

            self.measurement.save_data(filename2, slopestobesaved)
            self.measurement.save_data(filename3, heightstobesaved)
            self.show_warning("Slopes-Only Data saved!", f"Data saved into {filename2}, {filename3}")

        else:

            self.measurement.save_data(filename, self.results)
            self.measurement.save_data(filename2, slopestobesaved)
            self.measurement.save_data(filename3, heightstobesaved)

            self.show_warning("Full Data saved!", f"Data saved into {filename}, {filename2}, {filename3}")

    def endmeasurement(self):
        """Housekeeping after each single measurement"""
        self.motors.restartTimer()
        self.camViewer.camera.set_grab_nr(5)
        self.camViewer.start_grab()
        """ self.points = 0
        self.nrograbs = 5
        self.setpsize = 0.0
        self.length = 0.0"""

        # Clear input fields
        self.gui.points_input.clear()
        self.gui.length_input.clear()
        self.gui.stepsize_input.clear()
        self.gui.nrofgrabs_input.clear()

        act_speed = self.motors.X.getjogspeed()
        self.motors.X.setjogspeed(20)
        self.motors.xmove.move_abs(speed = "rapid", coord = float(self.xStartPos))
        self.show_warning("End of Measurement!", f"Stage at the original position. Jog speed set at {self.motors.X.getjogspeed()}")
        while True:
            if abs(self.xStartPos - self.motors.X.get_real_pos()) < 0.05:
                break
            time.sleep(0.075)
        self.motors.X.setjogspeed(act_speed)


    def stopMeasurement(self):
        # TODO: dump all the motors positions into a file. Then set the positions after homing to those values
        self.motors.stopall()
        self.motors.restartTimer()
        self.camera.set_grab_nr(5)
        autopos = self.motors.X.get_real_pos
        self.show_warning("Warning!", "Measurement interrupted")
        self.motors.
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
