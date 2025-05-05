import datetime
from itertools import filterfalse

from ControlCenter import Control_Utilities as cu
from ControlCenter.Control_Utilities import *
from ControlCenter.MultiThreading import *
from ControlCenter.Laser import *
from ControlCenter.Measurement import *
from ControlCenter.MotorControls import *
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

    def __init__(self, shell, motors = None ):
        #The motors object have to be passed by the caller, otherwise this won't work.
        if shell is not None:
            self.shell = shell
        else:
          self.shell = Utilities.connect2Pmac()
    # Initing objects for the measurements:
        self.motor_timer = QTimer()
        self.camera_timer = QTimer()
        if motors is not None:
            self.motors = motors
        else:
            self.motors = MotorControls(shell = self.shell)

        self.laser = Laser()
        self.measurement = Measurement()
        # Some sanity values:

        self.length = 0.0  # this is the length (in mm ) of the measurement
        self.points = 0  # these are the number of measurement points
        self.stepsize = 0.0  # this is the stepsize ( in mm) of the measurement
        self.nrofgrabs = 5  # default nr of camera grabs per measurement point
        self.xStartPos = 650000 # default @ middle of stage travel...
        self.today = datetime.datetime.now().strftime("%H-%M_%Y%m%d")

    # Create an instance of the Measurement_GUI class:
        super().__init__()
        self.gui = Ui_MeasurementGUI()
        self.gui.setupUi(self)


        # Dealing with the GUI:
        self.initCameraTab()
        self.initHeightTab()
        self.initSlopesTab()

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
        self.gui.stopButton.setEnabled(False)



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

        self.xStartPos = self.motors.messenger.coordinates["X"]
        mymessage = f"Set the measurement starting position @ {MathUtils.um2mm(self.XStartPos)}"
        self.warning.show_warning(title="Setting measurement start position!",
                                  message= mymessage)

    def get_all_motor_pos(self):
        """
        This spits out a formatted text. I think it's better creating a method rather than using inside the measure for cycle.
        :return: all_motor_pos.
        """
        return MotorControls.get_all_pos()

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
        print("Exposure time: ", self.camViewer.camera.camera.ExposureTime())
        print("Number of grabs per point: ", self.nrofgrabs)
        self.camViewer.stop_grab()

        if not self.conditions_check():
            return
        #print("Inside the StartMeasurement method: ")
        self.print_attributes()

        # Ensure points, length, and stepsize are set
        if self.points == 0 or self.length == 0.0 or self.stepsize == 0.0:
            self.show_warning("Missing Values!", "Please provide valid inputs for points, length, and stepsize.")
            return

        self.gui.startButton.setEnabled(False)
        self.gui.stopButton.setEnabled(True)

        self.results = self.writeheader()
        #print(self.results)
        #Instantiating the arrays for storing the results
        myposarray = np.array([])
        mystepposarray = np.array([])
        slopesarray = np.array([])
        heightsarray = np.array([])

        if not self.motors.messenger.coordinates["X"] - self.xStartPos > 1.0: # difference bigger than 1 micron
            print("Stage at starting position!")

        else:
            self.show_warning("Head moving", "Moving X Stage to starting position")
            self.motors.xmove.move_abs(speed = "rapid", coord = self.xStartPos)
        print("Stepsize set at: ", self.stepsize, "microns")

        # This below is the main measurement loop
        for i in range(self.points + 1):
            full_pos = self.pos_update()
            mypos = full_pos["X"]# this is in microns
            mysteppos = i * self.stepsize # this is in microns, a lot better for graphical representation.
            print("\n")
            print("Position ", i + 1, f" of {self.points + 1}")
            print("X Coordinate: ", mypos)
            label_message =  str(i + 1) + f" of {self.points}"
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

            self.results += (str(mypos) + "\t\t" + str(self.motors.messenger.coordinates["Y"]) +
                             "\t\t" + str(averageCentroidX) + "\t\t" + str(averageCentroidY) + "\n")

            myposarray = np.append(myposarray, mypos - self.xStartPos)

            mystepposarray = np.append(mystepposarray, mysteppos)
            nextpos = mypos + self.stepsize # all should be in microns

            if i != self.points:
                print("Moving stage to next position: ", nextpos)
                self.motors.xmove.move_rel(speed = "rapid", distance = self.stepsize)
                """while True:
                    if abs(nextpos - float(self.motors.messenger.coordinates["X"]))<=1:
                        break


                #self.motors.xmove.move_rel(speed = "rapid", distance= self.stepsize)
                i += 1
                averageCentroidX  = 0.0
                averageCentroidY = 0.0"""

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
        #self.motors.restartTimer()

        self.camViewer.camera.set_grab_nr(5)
        self.camViewer.start_grab()
        # Clear input fields
        self.gui.points_input.clear()
        self.gui.length_input.clear()
        self.gui.stepsize_input.clear()
        self.gui.nrofgrabs_input.clear()
        self.gui.startButton.setEnabled(True)
        self.gui.stopButton.setEnabled(False)

        act_speed = self.motors.X.jogspeed
        self.motors.X.setjogspeed(25)
        self.motors.xmove.move_abs(speed = "rapid", coord = float(self.xStartPos))
        self.show_warning("End of Measurement!", f"Stage at the original position.")
        self.motors.X.setjogspeed(act_speed)


    def pos_update(self):
        self.motors.messenger.pause()
        response = self.motors.messenger.get_and_update_coords()
        self.motors.messenger.update_coordinates(response)
        pos_update = self.motors.messenger.coordinates.copy()
        self.motors.messenger.resume()
        return(pos_update)

    def is_this_real (self):
        return("Mona")

    def stopMeasurement(self):
        # TODO: dump all the motors positions into a file. Then set the positions after homing to those values
        old_coords_dict = self.motors.get_all_pos()
        self.motors.stopall()
        #self.motors.restartTimer()
        self.camera.set_grab_nr(5)
        self.show_warning("Warning!", "Measurement interrupted")
        self.motors.MotorUtil.homeGantry()
        if self.motors.X.get_real_pos() != old_coords_dict["X"]:
            self.motors.xmove.moveabs(old_coords_dict["X"])
        if self.motors.Y.get_real_pos() != old_coords_dict["Y"]:
            self.motors.ymove.moveabs(old_coords_dict["Y"])
        if self.motors.Z.get_real_pos() != old_coords_dict["Z"]:
          self.motors.zmove.moveabs(old_coords_dict["Z"])
        if self.motors.roll.get_real_pos() != old_coords_dict["roll"]:
            self.motors.rollmove.moveabs(old_coords_dict["roll"])
        if self.motors.pitch.get_real_pos() != old_coords_dict["pitch"]:
            self.motors.pitchmove.moveabs(old_coords_dict["pitch"])
        if self.motors.yaw.get_real_pos() != old_coords_dict["yaw"]:
            self.motors.yawmove.moveabs(old_coords_dict["yaw"])
        self.gui.startButton.setEnabled(True)
        self.gui.stopButton.setEnabled(False)

    def setXstartPos(self):
        self.xStartPos = self.motors.messenger.coordinates["X"]
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

    def closeEvent(self, event):
        """Handle cleanup before closing the window."""
        reply = QMessageBox.question(
            self, "Exit Confirmation", "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.shell.close_connection()  # Close SSH connection if applicable
            self.camViewer.camera.closecam() #closes the Cam.
            event.accept()  # Allow the window to close
        else:
            event.ignore()  # Prevent the window from closing




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MeasurementControls(None)
    window.show()
    sys.exit(app.exec_())
