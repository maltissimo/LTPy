import datetime

import ControlCenter.MathUtils
from ControlCenter.Control_Utilities import *
from ControlCenter.MathUtils import MathUtils
from ControlCenter.Laser import *
from ControlCenter.Measurement import *
from ControlCenter.MotorControls import *
from Graphics.Base_Classes_graphics.Measurements_GUI import *
from Graphics.Base_Classes_graphics.RT_Dataplot import *
from Graphics.CameraViewer_MT import *
from PyQt5.QtCore import QCoreApplication

LENSFOCAL = 502.5  # this is the nominal focal length in mm of our lens
ZERO_X = 5280 / 2  # Have to start somewhere, this is half of camera.Width()
ZERO_Y = 4600 / 2  # Have to start somewhere, this is half of camera.Height()

STOP_WARNING = {"type": "Warning",
                "title" : "Measurement stopped!",
                "message" : "Measurement stopped by user!"}

class MeasurementControls(QMainWindow):
    f = LENSFOCAL  # this is now in mm
    X0 = ZERO_X
    Y0 = ZERO_Y

    def __init__(self, shell, motors = None , detector = None):
        #The motors object have to be passed by the caller, otherwise this won't work.
        if shell is not None:
            self.shell = shell
        else:
          self.shell = Utilities.connect2Pmac()
    # Initing objects for the measurements:
        if motors is not None:
            self.motors = motors
        else:
            self.motors = MotorControls(shell = self.shell)
        if detector is not None:
            self.detector = detector

        self.laser = Laser()
        self.measurement = Measurement()
        self.stability_meas_flag = False
        self.measurement_thread = None
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

        self.gui.points_input.returnPressed.connect(self.get_points)
        self.gui.length_input.returnPressed.connect(self.get_length)
        self.gui.stepsize_input.returnPressed.connect(self.get_stepsize)
        self.gui.nrofgrabs_input.returnPressed.connect(self.get_nrofgrabs)

        self.gui.startButton.clicked.connect(self.on_start_pressed)
        self.gui.stopButton.clicked.connect(self.on_stop_pressed)
        self.gui.xStartPos.clicked.connect(self.setXstartPos)
        self.gui.stopButton.setEnabled(False)

    def get_points(self):
        self.points = int(self.gui.points_input.text())
        self.gui.points_input.clear()
        points_message = str(self.points)
        self.gui.points_display.setText(points_message)
        self.measurement.points = self.points

    def get_length(self):
        my_mm_length = float(self.gui.length_input.text())
        self.length = ControlCenter.MathUtils.MathUtils.mm2um(my_mm_length)
        self.gui.length_input.clear()
        length_message = str(my_mm_length)
        self.gui.length_display.setText(length_message)
        self.measurement.length = self.length

    def get_stepsize(self):
        stepsize = float(self.gui.stepsize_input.text())
        self.stepsize = ControlCenter.MathUtils.MathUtils.mm2um(stepsize)
        self.gui.stepsize_input.clear()
        stepsize_message = str(stepsize)
        self.gui.stepsize_display.setText(stepsize_message)
        self.measurement.stepsize = self.stepsize

    def get_nrofgrabs(self):
        self.nrofgrabs = int(self.gui.nrofgrabs_input.text())
        self.gui.nrofgrabs_input.clear()
        grabs_message =str(self.nrofgrabs)
        self.gui.nrofgrabs_label_2.setText(grabs_message)
        self.measurement.nrofgrabs = self.nrofgrabs

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
            stepsize_message = str(MathUtils.um2mm(self.stepsize))
            self.gui.stepsize_display.setText(stepsize_message)
            #self.print_attributes()
            return True

        elif self.length!= 0.0 and self.points!= 0 and self.stepsize !=0.0:
            self.stepsize = self.length / self.points
            stepsize_message = str(MathUtils.um2mm(self.stepsize))
            self.gui.stepsize_display.setText(stepsize_message)
            #self.print_attributes()
            return True

        elif self.length ==0.0  or self.stepsize == 0.0 and self.points !=0:
            self.gui.stepsize_display.setText("0.0")
            self.stability_meas_flag = True
            self.show_warning(title = "Stability measurement!",
                              message = "Carriying out stability measurement.")
            """
            we pick from here and call a new method for the stability measurement
            First we kill the 
            """
            self.stability_measurement()


        else:
            self.show_warning(title = "Missing Values!",
                              message = "NEIN! At least two between Length, Step Size and Number of points are required")
            return False
        self.print_attributes()

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
        header += "Camera exposure time per point: " + str(self.camViewer.camera.camera.ExposureTime()) + " usec" + "\n"
        header += "Length of measurement (mm): " + str(MathUtils.um2mm(self.length)) +"\n"
        header += "Nr of measurement points + 1: " +  str(self.points + 1 ) + "\n"
        header += "Stepsize of measurement (mm): " + str(MathUtils.um2mm(self.stepsize)) + "\n"
        header += "\t" + "X" + "\t\t" + "Y" + "\t\t" + "Centroid X" + "\t\t" + "Centroid Y"+ "\n"
        header += "\n"
        return header

    def getXposfromfull(self):
        full_pos = self.pos_update()
        #print(full_pos)
        return( full_pos["X"])

    def startMeasurement(self):

        if not self.conditions_check():
            return


        self.measurement_thread.update_signal.emit({"type": "print_attributes"})

        self.results = self.writeheader()
        #print(self.results)
        #Instantiating the arrays for storing the results
        self.myposarray = np.array([])
        mystepposarray = np.array([])
        self.slopesarray = np.array([])
        self.heightsarray = np.array([])

        if not self.motors.messenger.coordinates["X"] - self.xStartPos > 1.0: # difference bigger than 1 micron
            self.measurement_thread.update_signal.emit({"type": "startPosOk"})

        else:
            self.measurement_thread.update_signal.emit({"type": "Warning",
                                                        "title": "Head moving",
                                                        "message": "Moving X stage to starting position"})

            self.motors.xmove.move_abs(speed = "rapid", coord = self.xStartPos)
        #print("Stepsize set at: ", self.stepsize, "microns")

        # This below is the main measurement loop
        for i in range(self.points + 1):
            if not self.measurement_thread.running:
                self.measurement_thread.update_signal.emit(STOP_WARNING)
                return

            mypos = self.getXposfromfull() # this is in microns
            mysteppos = i * self.stepsize # this is in microns, a lot better for graphical representation.
            self.measurement_thread.update_signal.emit({"type": "pos_update",
                                                        "step": i,
                                                        "x_coord": mypos})

            averageX= 0.0  # resetting back to 0 after each round of the loop below.
            averageY = 0.0

            for grab in range(self.nrofgrabs):
                if not self.measurement_thread.running:
                    self.save_data(self.myposarray, self.slopesarray, self.heightsarray)
                    self.measurement_thread.update_signal.emit({"type": "stop_measurement"})
                    self.measurement_thread.update_signal.emit(STOP_WARNING)
                    return

                image = self.camViewer.camera.acquire_once()
                self.measurement_thread.update_signal.emit({"type": "camimage",
                                                            "image": image})

                centroid = ControlCenter.MathUtils.MathUtils.centroid(image)

                averageX += centroid[1] # this is the HOR vector @ Y = centroid[1], i.e. parallel to HOR axis

                averageY += centroid[0] # this is the VERTICAL vector @ X = centroid[0], i.e. parallel to vertical axis

                #grab += 1

            averageCentroidX = averageX / self.nrofgrabs
            averageCentroidY = averageY / self.nrofgrabs


            slope = self.measurement.slope_calc(averageCentroidY) #changed for trial on 2024 12 20 MA, gave 14 urad with 100 grabs

            self.slopesarray = np.append(self.slopesarray, slope)

            self.results += (str(mypos) + "\t\t" + str(self.motors.messenger.coordinates["Y"]) +
                             "\t\t" + str(averageCentroidX) + "\t\t" + str(averageCentroidY) + "\n")

            self.myposarray = np.append(self.myposarray, mypos - self.xStartPos)

            mystepposarray = np.append(mystepposarray, mysteppos)
            nextpos = mypos + self.stepsize #all should be in microns
            #print("stepsize =  ", self.stepsize)

            if i != self.points:
                if not self.measurement_thread.running:
                    self.measurement_thread.update_signal.emit(STOP_WARNING)
                    return

                if self.stability_meas_flag == False:
                    update_message = "Moving stage to next position" + str(nextpos)
                    self.measurement_thread.update_signal.emit({"type": "next",
                                                                "message": update_message})
                    #print("Moving stage to next position: ", nextpos)
                    #print("@ pos: ", i)
                    self.motors.xmove.move_abs(coord = nextpos)
                    #self.motors.xmove.move_rel (distance = self.stepsize)
                    self.waitformoveend()

                elif self.stability_meas_flag == True:
                    """
                    need to kill the measurement_thread worker and start a
                    """
                    stab_message = "Measurement  " + str(i) +" taken"
                    self.measurement_thread.update_signal.emit({"type": "stabnext",
                                                                "message": stab_message})

        # Calculating heights:

        fit, radius = ControlCenter.MathUtils.MathUtils.my_fit(arrayX = self.myposarray, arrayY = self.slopesarray, order = 1)

        to_be_plotted = self.slopesarray - fit # this is the REAL measurement value

        self.heightsarray = self.measurement.height_calc(to_be_plotted, self.myposarray)



        #Calculating rms, then updating plots
        self.measurement.slopes_rms = ControlCenter.MathUtils.MathUtils.RMS(to_be_plotted)
        self.measurement.heights_rms = ControlCenter.MathUtils.MathUtils.RMS(self.heightsarray)
        roundslope = round(1000000 * self.measurement.slopes_rms, 3)
        roundheight = round(self.measurement.heights_rms, 3)


        end_message = "Radius as coeff[0], in m: " + str(radius / 1000000) + "\n"
        end_message += "RMS slope of the measurement:  " + str(roundslope) + " urad \n"
        end_message += "RMS height of the measurement: " + str(roundheight) + "um\n"
        self.measurement_thread.update_signal.emit({"type": "sumprint",
                                                    "message": end_message})



        self.measurement_thread.update_signal.emit({"type": "plot_update",
                                                    "x_array": mystepposarray,
                                                    "slopes": to_be_plotted,
                                                    "heights": self.heightsarray,
                                                    "roundslopes": roundslope,
                                                    "roundheights": roundheight
                                                    })

        self.measurement_thread.update_signal.emit({ "type": "end_measurement"
        })

    def save_data(self, myposarray, slopesarray, heightsarray):
        slopestobesaved = "Slope RMS: " + str(self.measurement.slopes_rms) + "\n"
        heightstobesaved = "Height RMS: " + str(self.measurement.heights_rms) + "\n"
        slopestobesaved += self.measurement.pretty_printing(myposarray, slopesarray)
        heightstobesaved += self.measurement.pretty_printing(myposarray, heightsarray)

        filename = "FullData" + self.today + ".txt"
        filename2 = "Xpos_slopes" + self.today + ".txt"
        filename3 = "Xpos_heights" + self.today + ".txt"

        if self.gui.savelldata.isChecked():
            self.measurement.save_data(filename2, slopestobesaved)
            self.measurement.save_data(filename3, heightstobesaved)
            """self.measurement_thread.update_signal.emit({"type" : "Warning",
                                                        "title" : "Slopes-Only Data saved!",
                                                        "message": f"Data saved into {filename2}, {filename3}"
                                                        })"""
            self.show_warning("Slopes-Only Data saved!", f"Data saved into {filename2}, {filename3}")

        else:

            self.measurement.save_data(filename, self.results)
            self.measurement.save_data(filename2, slopestobesaved)
            self.measurement.save_data(filename3, heightstobesaved)
            """self.measurement_thread.update_signal.emit({"type": "Warning",
                                                        "title" : "Full Data saved!",
                                                        "message": f"Data saved into {filename}, {filename2}, {filename3}"
            })"""

            self.show_warning("Full Data saved!", f"Data saved into {filename}, {filename2}, {filename3}")

    def on_start_pressed(self):
        if self.measurement_thread is None or not self.measurement_thread.isRunning():
            #Moving all the GUI-related pre-measurement ops here, in order to avoid clashes between GUI updates and worker threads
            self.gui.startButton.setEnabled(False)
            self.gui.stopButton.setEnabled(True)
            self.camViewer.stop_grab()
            self.slopes_plot.clearPlot()
            self.height_plot.clearPlot()
            self.camViewer.camera.set_grab_nr(1)
            self.camViewer.camera.set_exp_time(self.camViewer.camera.camera.ExposureTime())
            #print("Exposure time: ", self.camViewer.camera.camera.ExposureTime())
            #print("Number of grabs per point: ", self.nrofgrabs)
            self.measurement_thread = WorkerThread(self.startMeasurement)
            self.measurement_thread.end_signal.connect(self.endmeasurement)
            self.measurement_thread.update_signal.connect(self.on_update)
            self.measurement_thread.start()

    def on_stop_pressed(self):
        if self.measurement_thread and self.measurement_thread.isRunning():
            self.measurement_thread.stop()
            self.stopMeasurement()

    def on_update(self, data):

        #print(f"on_update received: {data} ({type(data)})")

        if not isinstance(data, dict) or "type" not in data:
            return

        msg_type = data["type"]
        #print(f"Parsed msg_type: {msg_type}")

        if msg_type == "print_attributes":
            self.print_attributes()

        if msg_type == "Warning":
            warning = myWarningBox(title = data["title"],
                                        message = data["message"])
            warning.show_warning()

        if msg_type == "startPosOk":
            print("Stage at starting position!")

        if msg_type == "camimage":
            self.camViewer.camera.frame = data["image"]

        if msg_type == "pos_update":
            position = data["step"] + 1
            print("Position ", position, f" of {self.points +1}")
            print("X Coordinate: ", data["x_coord"])
            label_message = str(position) + f" of {self.points +1}"
            self.gui.step_label.setText(label_message)
            self.gui.xcoord_value_label.setText(str(data["x_coord"]))

        if msg_type == "next":
            print(data["message"])

        if msg_type == "stabnext":
            print(data["message"])

        if msg_type == "sumprint":
            print(data["message"])

        if msg_type == "plot_update":
            slope_label = self.slopes_plot.writeLabel(type="RMS Slopes", value=data["roundslopes"], units="urad")
            height_label = self.height_plot.writeLabel(type="RMS Heights", value=data["roundheights"], units="um")
            for i in range(len(data["heights"])):
                self.slopes_plot.updatePlot(data["x_array"][i]/1000, data["slopes"][i])
                self.height_plot.updatePlot(data["x_array"][i]/1000, data["heights"][i])
            self.slopes_plot.setCustomLabel(slope_label)
            self.height_plot.setCustomLabel(height_label)

        if msg_type == "get_save_dir":
            self.measurement.get_save_directory()

        if msg_type == "end_measurement" :
            self.endmeasurement()

        elif msg_type == "stop_measurement":
            self.on_measurement_stopped()
        #else:
            #print(f"Unknown data type: {msg_type}")

    def endmeasurement(self):
        """Housekeeping after each single measurement"""
        self.motors.messenger.pause()
        if self.measurement_thread is not None:
            try:
                self.measurement_thread.update_signal.disconnect()
                self.measurement_thread.end_signal.disconnect()
            except TypeError:
                # Already disconnected
                pass
            self.measurement_thread.running = False
            self.measurement_thread = None
        #print("Thread killed")
        # Saving the data:
        self.measurement.get_save_directory() # This updates the self.directory attribute
        self.save_data(self.myposarray, self.slopesarray, self.heightsarray)

        act_speed = self.motors.X.jogspeed
        self.motors.X.setjogspeed(25)
        self.motors.xmove.move_abs(speed = "rapid", coord = float(self.xStartPos))
        self.show_warning("End of Measurement!", f"Stage at the original position.")
        self.motors.X.setjogspeed(act_speed)
        self.motors.messenger.resume()
        self.clear_gui()


    def clear_gui(self):
        """
        This is to reset the GUI after a measurement has finished or has stopped:
        :return:
        """
        #re-set camera:
        self.camViewer.camera.set_grab_nr(5)
        self.camViewer.start_grab()
        # Clear input fields
        self.gui.points_input.clear()
        self.gui.length_input.clear()
        self.gui.stepsize_input.clear()
        self.gui.nrofgrabs_input.clear()
        self.gui.startButton.setEnabled(True)
        self.gui.stopButton.setEnabled(False)

    def pos_update(self):
        self.motors.messenger.pause()
        response = self.motors.messenger.get_and_update_coords()
        self.motors.messenger.update_coordinates(response)
        pos_update = self.motors.messenger.coordinates.copy()
        self.motors.messenger.resume()
        return(pos_update)

    def waitformoveend(self):
        while not self.motors.xmove.movecomplete:
            time.sleep(0.05)
            QCoreApplication.processEvents()  # allows Qt signals to be processe
        time.sleep(0.05)

    def on_measurement_stopped(self):
        # TODO: dump all the motors positions into a file. Then set the positions after homing to those values
        old_coords_dict = self.motors.get_all_pos()
        self.motors.stopall()
        self.measurement_thread.stop()
        self.camera.camera.set_grab_nr(5)
        self.show_warning("Warning!", "Measurement interrupted")
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
        self.clear_gui()

    def setXstartPos(self):
        self.xStartPos = self.motors.messenger.coordinates["X"]
        self.show_warning("Warning!", "Measurement starting position set!")

    def initHeightTab(self):
        self.height_plot = RealTime_plotter()

        self.height_plot.setLabels(bottom_label = "X position", bottom_units = "mm", left_label="Heights", left_units = "um")
        self.height_plot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        height_layout = QtWidgets.QVBoxLayout(self.gui.height_tab)
        height_layout.addWidget(self.height_plot)

        self.gui.height_tab.setLayout(height_layout)

    def initSlopesTab(self):
        self.slopes_plot = RealTime_plotter()
        slopes_layout = QtWidgets.QVBoxLayout(self.gui.Slopes_tab)
        slopes_layout.addWidget(self.slopes_plot)
        self.gui.Slopes_tab.setLayout(slopes_layout)
        self.slopes_plot.setLabels(bottom_label = "X position", bottom_units = "mm", left_label="Slope", left_units = "rad")

        self.slopes_plot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


    def initCameraTab(self):

        self.camViewer = CamViewer(self.detector)

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

        if shell.alive:  # Check if the shell is alive
            self.shell.close_connection()  # Close SSH connection if applicable
        self.camViewer.camera.closecam() #closes the Cam.
        event.accept()  # Allow the window to close
        event.ignore()  # Prevent the window from closing




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MeasurementControls(None)
    window.show()
    sys.exit(app.exec_())
