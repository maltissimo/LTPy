from ControlCenter.Control_Utilities import *
from ControlCenter.Laser import *
from ControlCenter.Measurement import *
from ControlCenter.MotorControls import *
from ControlCenter.MultiThreading import WorkerThread
from Graphics.Base_Classes_graphics.Measurements_GUI2 import *
from ControlCenter.CameraViewer_MT import *
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIntValidator
from Graphics.Base_Classes_graphics.RT_Dataplot import *

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
        self.run_backward = False
        # Some sanity values:

        self.length = 0.0  # this is the length (in mm ) of the measurement
        self.points = 0  # these are the number of measurement points
        self.stepsize = 0.0  # this is the stepsize ( in mm) of the measurement
        self.nrofgrabs = 5  # default nr of camera grabs per measurement point
        self.xStartPos = None # default, set at startMeasurement if user didn't set...
        self.today = datetime.datetime.now().strftime("%H-%M_%Y%m%d")


    # Create an instance of the Measurement_GUI class:
        super().__init__()
        self.gui = Ui_MeasurementGUI()
        print("GUI inited")
        self.gui.setupUi(self)


        # Dealing with the GUI:
        self.initCameraTab()
        print("Camera tab inited")
        self.initHeightTab()
        print("Height tab inited")
        self.initSlopesTab()
        print("Slopes tab inited")

        self.gui.points_input.returnPressed.connect(self.get_points)
        self.gui.length_input.returnPressed.connect(self.get_length)
        self.gui.stepsize_input.returnPressed.connect(self.get_stepsize)
        self.gui.nrofgrabs_input.returnPressed.connect(self.get_nrofgrabs)
        self.gui.height_lineedit.returnPressed.connect(self.set_acq_size)
        self.gui.width_lineedit.returnPressed.connect(self.set_acq_size)

        self.gui.startButton.clicked.connect(self.on_start_pressed)
        self.gui.stopButton.clicked.connect(self.on_stop_pressed)
        self.gui.xStartPos.clicked.connect(self.setxStartPos)
        self.gui.acq_size_set.clicked.connect(self.set_acq_size)

        self.gui.stopButton.setEnabled(False)
        print("logics inited")

        #Integer validation

        self.gui.width_lineedit.setValidator(QIntValidator(48, 5280))
        self.gui.height_lineedit.setValidator(QIntValidator(4, 4600))

        # Some settings:
        frame_text = "4600x5280 px (W x H)"
        self.gui.frame_size_label.setText(frame_text)
        self.gui.nrofgrabs_display.setText(str("Not set!"))
        self.gui.length_display.setText(str("Not set!"))
        self.gui.stepsize_display.setText(str("Not set!"))
        self.gui.points_display.setText(str("Not set!"))

    def set_acq_size(self):
        mewidth = None
        meheight = None

        # Check Width Input
        width_text = self.gui.width_lineedit.text()
        if width_text:
            try:
                mewidth = int(width_text)
                self.gui.width_lineedit.clear()
            except ValueError:
                pass

        # Check Height Input
        height_text = self.gui.height_lineedit.text()
        if height_text:
            try:
                meheight = int(height_text)
                self.gui.height_lineedit.clear()
            except ValueError:
                pass

        # Only call set_roi if at least one value is present
        if mewidth is not None or meheight is not None:
            self.camViewer.camera.set_roi(width=mewidth, height=meheight)
            
            # Update label with current camera values
            # Note: Accessing GetValue() might be Pylon specific, using the wrapper methods is safer if available
            # or just reading back the properties we set if the camera object updates them.
            # Assuming self.camViewer.camera.width and .height are updated in set_roi
            current_w = self.camViewer.camera.width
            current_h = self.camViewer.camera.height
            me_text = f"{current_h} x {current_w} H x W"
            self.gui.frame_size_label.setText(me_text)

    def get_points(self):
        self.points = int(self.gui.points_input.text())
        self.gui.points_input.clear()
        points_message = str(self.points)
        self.gui.points_display.setText(points_message)
        self.measurement.points = self.points

    def get_length(self):
        my_mm_length = float(self.gui.length_input.text())
        self.length = MathUtils.mm2um(my_mm_length)
        self.gui.length_input.clear()
        length_message = str(my_mm_length)
        self.gui.length_display.setText(length_message)
        self.measurement.length = self.length

    def get_stepsize(self):
        stepsize = float(self.gui.stepsize_input.text())
        self.stepsize = MathUtils.mm2um(stepsize)
        self.gui.stepsize_input.clear()
        stepsize_message = str(stepsize)
        self.gui.stepsize_display.setText(stepsize_message)
        self.measurement.stepsize = self.stepsize

    def get_nrofgrabs(self):
        self.nrofgrabs = int(self.gui.nrofgrabs_input.text())
        self.gui.nrofgrabs_input.clear()
        grabs_message =str(self.nrofgrabs)
        self.gui.nrofgrabs_display.setText(grabs_message)
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

    def setxStartPos(self):

        self.xStartPos = self.motors.messenger.coordinates["X"]
        mymessage = f"Set the measurement starting position @ {MathUtils.um2mm(self.xStartPos)}"
        self.show_warning(title="Setting measurement start position!",
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

        header = ""
        header += "Date of measurement: " + self.today + "\n"
        header += "Nr of camera grabs per point: " + str(self.nrofgrabs) + "\n"
        header += "Camera exposure time per point: " + str(
            self.camViewer.camera.camera.ExposureTime()) + " [\u00B5sec]\n"
        header += "Length of measurement : " + str(MathUtils.um2mm(self.length)) + " [mm]\n"
        header += "Nr of measurement points + 1: " + str(self.points + 1) + "\n"
        header += "Stepsize of measurement: " + str(MathUtils.um2mm(self.stepsize)) + " [mm]\n"
        header += "Laser intensity preset: " + str(float(self.laser.pow_level) * 1000) + " [mW]\n"
        header += "Slope RMS: {{slope_rms}} [\u00B5rad]\n"
        header += "Height RMS: {{height_rms}} [\u00B5m]\n"
        header += "Radius from fit: {{radius}} [m]\n"

        # 21 Columns: FWD, BWD, AVG for each of the 7 attributes
        cols = [
            "X [FWD] position", "X [BWD] position", "X [AVG] position",
            "Y [FWD] position", "Y [BWD] position", "Y [AVG] position",
            "CentroidX [FWD]", "CentroidX [BWD]", "CentroidX [AVG]",
            "CentroidY [FWD]", "CentroidY [BWD]", "CentroidY [AVG]",
            "Raw Slope [FWD][rad]", "Raw Slope [BWD][rad]", "Raw Slope [AVG][rad]",
            "Slope Error [FWD][rad]", "Slope Error [BWD][rad]", "Slope Error [AVG][rad]",
            "Height [FWD][\u00B5m]", "Height [BWD][\u00B5m]", "Height [AVG][\u00B5m]"
        ]
        header += "\t".join(cols) + "\n\n"
        return header

    def getXposfromfull(self):
        full_pos = self.pos_update()
        #print(full_pos)
        return( full_pos["X"])

    def clear_console(self):
        print("\033[H\033[J", end="")
        print("Console cleared, new measurement starting.")

    def generate_data_string(self):
        """
        Commented out due to recurring indexing error at the end of the  measurement loop: 
        MA 20260827
        
        # Safety check for array lengths to avoid index errors
        limit = min(len(self.myposarray), len(self.y_pos_list), len(self.centroid_x_list), len(self.centroid_y_list), len(self.slopesarray))
        
        """
        data_str = ""
        n_points = len(self.myposarray)
        if n_points == 0:
            return data_str

        has_bwd = getattr(self, "has_bwd_data", False)
        x_start = self.xStartPos if self.xStartPos is not None else 0.0

        for i in range(n_points):
            # X Coordinates
            x_fwd = self.pos_fwd[i] + x_start
            x_bwd = (self.pos_bwd_rev[i] + x_start) if has_bwd else x_fwd
            x_avg = self.myposarray[i] + x_start

            # Y Positions
            y_fwd = self.y_fwd[i]
            y_bwd = self.y_bwd_rev[i] if has_bwd else y_fwd
            y_avg = self.y_pos_list[i]

            # Centroids
            cx_fwd = self.cx_fwd[i]
            cx_bwd = self.cx_bwd_rev[i] if has_bwd else cx_fwd
            cx_avg = self.centroid_x_list[i]

            cy_fwd = self.cy_fwd[i]
            cy_bwd = self.cy_bwd_rev[i] if has_bwd else cy_fwd
            cy_avg = self.centroid_y_list[i]

            # Raw Slopes
            s_raw_fwd = self.slopes_fwd[i]
            s_raw_bwd = self.slopes_bwd_rev[i] if has_bwd else s_raw_fwd
            s_raw_avg = self.slopesarray[i]

            # Slope Errors (residuals)
            s_err_fwd = self.slope_err_fwd[i] if i < len(self.slope_err_fwd) else 0.0
            s_err_bwd = (self.slope_err_bwd[i] if i < len(self.slope_err_bwd) else 0.0) if has_bwd else s_err_fwd
            s_err_avg = self.slopes_to_be_plotted[i] if i < len(self.slopes_to_be_plotted) else 0.0

            # Heights
            h_fwd = self.heights_fwd[i] if i < len(self.heights_fwd) else 0.0
            h_bwd = (self.heights_bwd[i] if i < len(self.heights_bwd) else 0.0) if has_bwd else h_fwd
            h_avg = self.heightsarray[i] if i < len(self.heightsarray) else 0.0

            row = [
                f"{x_fwd:.4f}", f"{x_bwd:.4f}", f"{x_avg:.4f}",
                f"{y_fwd:.4f}", f"{y_bwd:.4f}", f"{y_avg:.4f}",
                f"{cx_fwd:.4f}", f"{cx_bwd:.4f}", f"{cx_avg:.4f}",
                f"{cy_fwd:.4f}", f"{cy_bwd:.4f}", f"{cy_avg:.4f}",
                f"{s_raw_fwd:.9e}", f"{s_raw_bwd:.9e}", f"{s_raw_avg:.9e}",
                f"{s_err_fwd:.9e}", f"{s_err_bwd:.9e}", f"{s_err_avg:.9e}",
                f"{h_fwd:.6e}", f"{h_bwd:.6e}", f"{h_avg:.6e}"
            ]
            data_str += "\t".join(row) + "\n"

        return data_str

    def _run_single_scan(self, direction="FORWARD"):
        pos_list = []
        slopes_list = []
        y_list = []
        cx_list = []
        cy_list = []

        for i in range(self.points + 1):
            if not self.measurement_thread.running:
                return None

            mypos = self.getXposfromfull()
            self.measurement_thread.update_signal.emit({
                "type": "pos_update",
                "step": i,
                "x_coord": mypos
            })

            self.averageX = 0.0
            self.averageY = 0.0
            image = None

            for grab in range(self.nrofgrabs):
                if not self.measurement_thread.running:
                    return None

                image = self.camViewer.camera.grabdata()
                if image is not None:
                    #centroid = MathUtils.centroid(image)
                    centroid = MathUtils.compute_ltp_centroid(image)
                    self.averageX += centroid[0]
                    self.averageY += centroid[1]

            if image is not None:
                self.measurement_thread.update_signal.emit({
                    "type": "camimage",
                    "image": image
                })

            avg_cx = self.averageX / self.nrofgrabs
            avg_cy = self.averageY / self.nrofgrabs
            slope = self.measurement.slope_calcX(avg_cy)

            rel_pos = mypos - self.xStartPos
            pos_list.append(rel_pos)
            slopes_list.append(slope)
            y_list.append(self.motors.messenger.coordinates["Y"])
            cx_list.append(avg_cx)
            cy_list.append(avg_cy)

            # Live plot rendering
            if direction == "FORWARD":
                if len(slopes_list) >= 2:
                    cur_pos = np.array(pos_list)
                    cur_slopes = np.array(slopes_list)
                    fit, _ = MathUtils.my_fit(cur_pos, cur_slopes, order=1)
                    fitted_slopes = cur_slopes - fit
                    heights = self.measurement.height_calc(fitted_slopes, cur_pos)

                    self.measurement_thread.update_signal.emit({
                        "type": "meas_plot_update",
                        "x_array": cur_pos,
                        "raw_slopes": cur_slopes,
                        "fitted_slopes": fitted_slopes,
                        "heights": heights
                    })
            else:
                if len(slopes_list) >= 2:
                    cur_pos = np.array(pos_list)
                    cur_slopes = np.array(slopes_list)
                    fit_bwd, _ = MathUtils.my_fit(cur_pos, cur_slopes, order=1)
                    fitted_bwd = cur_slopes - fit_bwd
                else:
                    cur_pos = np.array(pos_list)
                    fitted_bwd = np.zeros_like(cur_pos)
                # Emit backward points to the dedicated green trace
                self.measurement_thread.update_signal.emit({
                    "type": "meas_bwd_plot_update",
                    "x_bwd": np.array(pos_list),
                    "fitted_bwd": fitted_bwd
                })

            # Motion to next coordinate
            if i < self.points:
                if not self.measurement_thread.running:
                    return None

                nextpos = (mypos + self.stepsize) if direction == "FORWARD" else (mypos - self.stepsize)
                self.measurement_thread.update_signal.emit({
                    "type": "next",
                    "message": f"[{direction}] Moving stage to next position {nextpos}"
                })
                self.motors.xmove.move_abs(coord=nextpos)
                if direction == "FORWARD":
                    time.sleep(0.8) # some time to settle the stage...
                elif direction == "BACKWARD":
                    time.sleep(0.8)

        return (np.array(pos_list), np.array(slopes_list), y_list, cx_list, cy_list)

    def _no_data(self):
        self.results = self.header_str + self.generate_data_string()
        self.save_data(self.myposarray, self.slopesarray, self.slopes_to_be_plotted, self.heightsarray)
        self.measurement_thread.update_signal.emit({"type": "stop_measurement"})
        self.measurement_thread.update_signal.emit(STOP_WARNING)
        return
    def _measurement_diagnostics(self,
                                 pos_forward,
                                 pos_backward,
                                 slopes_forward,
                                 slopes_backward_rev,
                                 ):

        pos_diff = pos_forward - pos_backward[::-1]
        print("Max positional discrepancy between FWD and BWD:", np.max(np.abs(pos_diff)))

        fit_fwd, rad_fwd = MathUtils.my_fit(pos_forward, slopes_forward, order=1)
        err_fwd = slopes_forward - fit_fwd

        fit_bwd, rad_bwd = MathUtils.my_fit(pos_backward[::-1], slopes_backward_rev, order=1)
        err_bwd = slopes_backward_rev - fit_bwd

        rms_fwd = 1e6 * MathUtils.RMS(self.measurement.FOP_smoothing(err_fwd))
        rms_bwd = 1e6 * MathUtils.RMS(self.measurement.FOP_smoothing(err_bwd))

        err_avg = 0.5 * (err_fwd + err_bwd)
        rms_avg_detrended = 1e6 * MathUtils.RMS(self.measurement.FOP_smoothing(err_avg))

        print(f"\n--- DIAGNOSTICS ---")
        print(f"FWD Detrended RMS:     {rms_fwd:.3f} \u00B5rad (R = {rad_fwd / 1e6:.3f} m)")
        print(f"BWD Detrended RMS:     {rms_bwd:.3f} \u00B5rad (R = {rad_bwd / 1e6:.3f} m)")
        print(f"Avg of Detrended RMS:  {rms_avg_detrended:.3f} \u00B5rad")
        print(f"Max coordinate offset: {np.max(np.abs(pos_forward - pos_backward[::-1])):.2f} \u00B5m")
        print(f"-------------------\n")
        # =====================================================================
        return

    def startMeasurement(self):
        if not self.conditions_check():
            return

        self.measurement_thread.update_signal.emit({"type": "print_attributes"})
        self.header_str = self.writeheader()
        self.results = self.header_str

        if self.xStartPos is None:
            self.xStartPos = self.getXposfromfull()
        elif not self.motors.messenger.coordinates["X"] - self.xStartPos > 50.0:
            self.measurement_thread.update_signal.emit({"type": "startPosOk"})
        else:
            self.measurement_thread.update_signal.emit({
                "type": "Warning",
                "title": "Head moving",
                "message": "Moving X stage to starting position"
            })
            self.motors.xmove.move_abs(speed="rapid", coord=self.xStartPos)

        # 1. FORWARD SCAN
        self.measurement_thread.update_signal.emit({
            "type": "next",
            "message": "Starting FORWARD scan..."
        })
        fwd_data = self._run_single_scan(direction="FORWARD")
        if fwd_data is None:
            self._no_data(self)
            return

        self.pos_fwd, self.slopes_fwd, self.y_fwd, self.cx_fwd, self.cy_fwd = fwd_data

        if self.slopes_fwd.size >= 2:
            fit_fwd, rad_fwd = MathUtils.my_fit(arrayX=self.pos_fwd, arrayY=self.slopes_fwd, order=1)
            self.slope_err_fwd = self.slopes_fwd - fit_fwd
            self.heights_fwd = self.measurement.height_calc(self.slope_err_fwd, self.pos_fwd)
            slope_err_fwd_smooth = self.measurement.FOP_smoothing(self.slope_err_fwd)
            fwd_slope_rms = round(1e6 * MathUtils.RMS(slope_err_fwd_smooth), 3)
            text = "\n" + "=" * 50 + "\n"
            text += f"FORWARD SCAN FINISHED:"
            text += f"  Radius: {rad_fwd / 1e6:.4f} m"+ "\n"
            text += f"  Slope Error RMS: {fwd_slope_rms} \u00B5rad"+ "\n"
            #text += f"  Slope Error RMS smoothed  [rad]:\n{slope_err_fwd_smooth}"+ "\n"
            text += "\n" + "=" * 50 + "\n"
            self.measurement_thread.update_signal.emit({
                "type" : "next",
                "message" : text})
            text = []

        # 2. BACKWARD SCAN
        run_bwd = getattr(self, "run_backward", False)
        self.has_bwd_data = False

        if run_bwd:
            # Settle mechanical backlash / carriage turnaround
            time.sleep(0.2)
            self.measurement_thread.update_signal.emit({
                "type": "next",
                "message": "Starting BACKWARD scan..."
            })
            bwd_data = self._run_single_scan(direction="BACKWARD")

            if bwd_data is None:
                self._no_data()
                return

            pos_bwd, slopes_bwd, y_bwd, cx_bwd, cy_bwd = bwd_data

            # Reverse backward data array indices to align with 0 -> L coordinates
            self.pos_bwd_rev = pos_bwd[::-1]
            self.slopes_bwd_rev = slopes_bwd[::-1]
            self.cx_bwd_rev = cx_bwd[::-1]
            self.cy_bwd_rev = cy_bwd[::-1]
            self.y_bwd_rev = y_bwd[::-1]
            self.has_bwd_data = True

            # =====================================================================
            # INSERT DIAGNOSTICS HERE
            # =====================================================================
            self._measurement_diagnostics( pos_forward = self.pos_fwd,
                                           pos_backward = pos_bwd,
                                           slopes_forward= self.slopes_fwd,
                                           slopes_backward_rev=self.slopes_bwd_rev)

            # Fit individual backward scan
            if self.slopes_bwd_rev.size >= 2:
                fit_bwd, rad_bwd = MathUtils.my_fit(self.pos_bwd_rev, self.slopes_bwd_rev, order=1)
                self.slope_err_bwd = self.slopes_bwd_rev - fit_bwd
                self.heights_bwd = self.measurement.height_calc(self.slope_err_bwd, self.pos_bwd_rev)
            else:
                self.slope_err_bwd = np.zeros_like(self.slopes_bwd_rev)
                self.heights_bwd = np.zeros_like(self.slopes_bwd_rev)

            # Averages
            self.myposarray = self.pos_fwd
            self.slopesarray = 0.5 * (self.slopes_fwd + self.slopes_bwd_rev)
            self.centroid_x_list = [0.5 * (a + b) for a, b in zip(self.cx_fwd, self.cx_bwd_rev)]
            self.centroid_y_list = [0.5 * (a + b) for a, b in zip(self.cy_fwd, self.cy_bwd_rev)]
            self.y_pos_list = [0.5 * (a + b) for a, b in zip(self.y_fwd, self.y_bwd_rev)]

        else:
            self.myposarray = self.pos_fwd
            self.slopesarray = self.slopes_fwd
            self.centroid_x_list = self.cx_fwd
            self.centroid_y_list = self.cy_fwd
            self.y_pos_list = self.y_fwd
            self.pos_bwd_rev = self.pos_fwd
            self.slopes_bwd_rev = self.slopes_fwd
            self.cx_bwd_rev = self.cx_fwd
            self.cy_bwd_rev = self.cy_fwd
            self.y_bwd_rev = self.y_fwd
            self.slope_err_bwd = self.slope_err_fwd
            self.heights_bwd = self.heights_fwd

        mystepposarray = np.arange(self.points + 1) * self.stepsize

        # 3. FINAL PROFILE RECONSTRUCTION ON AVERAGED DATA
        if self.slopesarray.size >= 2:
            fit, radius = MathUtils.my_fit(arrayX=self.myposarray, arrayY=self.slopesarray, order=1)
            self.slopes_to_be_plotted = self.slopesarray - fit
            self.heightsarray = self.measurement.height_calc(self.slopes_to_be_plotted, self.myposarray)
            to_be_plotted_smooth = self.measurement.FOP_smoothing(self.slopes_to_be_plotted)

            self.measurement.slopes_rms = MathUtils.RMS(to_be_plotted_smooth)
            self.measurement.heights_rms = MathUtils.RMS(self.heightsarray)
            roundslope = round(1000000 * self.measurement.slopes_rms, 3)
            roundheight = round(self.measurement.heights_rms, 3)
        else:
            radius, roundslope, roundheight = 0.0, 0.0, 0.0
            to_be_plotted_smooth = self.slopesarray
            self.slopes_to_be_plotted = self.slopesarray
            self.heightsarray = np.zeros_like(self.slopesarray)

        end_message = "Radius as coeff[0], in m: " + str(radius / 1000000) + "\n"
        end_message += "RMS slope of the measurement:  " + str(roundslope) + " \u00B5rad \n"
        end_message += "RMS height of the measurement: " + str(roundheight) + "\u00B5m\n"

        self.header_str = self.header_str.replace("{{slope_rms}}", f"{roundslope}")
        self.header_str = self.header_str.replace("{{height_rms}}", f"{roundheight}")
        self.header_str = self.header_str.replace("{{radius}}", f"{radius / 1000000}")
        self.results = self.header_str + self.generate_data_string()

        self.measurement_thread.update_signal.emit({"type": "sumprint", "message": end_message})

        # Redraw final detrended curve and heights calculated from the average
        self.measurement_thread.update_signal.emit({
            "type": "final_plot_update",
            "x_array": mystepposarray,
            "slopes": to_be_plotted_smooth,
            "heights": self.heightsarray,
            "roundslopes": roundslope,
            "roundheights": roundheight
        })

        self.save_data(self.myposarray, self.slopesarray, self.slopes_to_be_plotted, self.heightsarray)

        # 4. CARRIAGE RETURN (Only if single scan)
        if not run_bwd and self.xStartPos is not None:
            update_message = f"Returning stage to starting position: {self.xStartPos} um"
            self.measurement_thread.update_signal.emit({"type": "next", "message": update_message})
            act_speed = getattr(self.motors.X, "jogspeed", 25)
            self.motors.X.setjogspeed(25)
            self.motors.xmove.move_abs(speed="rapid", coord=float(self.xStartPos))
            self.motors.X.setjogspeed(act_speed)

        self.measurement_thread.update_signal.emit({"type": "end_measurement"})

    def save_data(self, myposarray, slopesarray, fittedslopesarray, heightsarray):
        if myposarray.size == 0:
            print("Warning: No data to save. Measurement may have been stopped or failed.")
            return
            
        slopestobesaved = "Slope RMS: " + str(self.measurement.slopes_rms) + "\n"
        heightstobesaved = "Height RMS: " + str(self.measurement.heights_rms) + "\n"
        slopestobesaved += self.measurement.pretty_printing(myposarray, slopesarray, fittedslopesarray)
        heightstobesaved += self.measurement.pretty_printing(myposarray, heightsarray)

        filename = "FullData" + self.today + ".txt"
        filename2 = "Xpos_slopes" + self.today + ".txt"
        filename3 = "Xpos_heights" + self.today + ".txt"

        if self.gui.savealldata.isChecked():
            self.measurement.save_data(filename, self.results)
            self.measurement.save_data(filename2, slopestobesaved)
            self.measurement.save_data(filename3, heightstobesaved)

            print(f"Full Data saved into {filename}, {filename2}, {filename3}")
        else:
            self.measurement.save_data(filename2, slopestobesaved)
            self.measurement.save_data(filename3, heightstobesaved)

            print( f" Slopes-OnlyData saved into {filename2}, {filename3}")

    def on_start_pressed(self):
        if self.measurement_thread is None or not self.measurement_thread.isRunning():
            self.run_backward = self.gui.run_backward_checkbox.isChecked()
            #Moving all the GUI-related pre-measurement ops here, in order to avoid clashes between GUI updates and worker threads
            self.gui.startButton.setEnabled(False)
            self.gui.stopButton.setEnabled(True)
            self.camViewer.stop_while_measuring()
            self.camViewer.camera.camera.StopGrabbing() # Commented out on 20250729 for testing self.camViewer.camera.grabdata() in startMeasurement method
            self.slopes_plot.clearPlot()
            if hasattr(self, 'slopes_bwd_plot'):
                self.slopes_bwd_plot.clearData()
            self.height_plot.clearPlot()
            self.measurement.get_save_directory()  # This updates the self.directory attribute
            self.camViewer.camera.set_grab_nr(1)
            self.camViewer.camera.set_exp_time(self.camViewer.camera.camera.ExposureTime())
            #print("Exposure time: ", self.camViewer.camera.camera.ExposureTime())
            #print("Number of grabs per point: ", self.nrofgrabs)
            self.camViewer.camera.start_continuous_grabbing()
            self.measurement_thread = WorkerThread(self.startMeasurement)
            self.measurement_thread.end_signal.connect(self.endmeasurement)
            self.measurement_thread.update_signal.connect(self.on_update)
            self.measurement_thread.error_signal.connect(self.on_thread_error) # Added error connection
            self.measurement_thread.start()

    def on_thread_error(self, error_msg):
        print(f"Measurement Thread Error: {error_msg}")
        self.show_warning("Measurement Error", f"An error occurred during measurement:\n{error_msg}")

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
            self.camViewer.display_image(data["image"])
            self.camViewer.display_fwhm(data["image"])
            self.camViewer.display_centroid(data["image"])

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

        if msg_type == "final_plot_update":
            self.slopesarray_plot.clearData()
            if hasattr(self, 'slopes_bwd_plot'):
                self.slopes_bwd_plot.clearData()
            self.fittedslopes_plot.clearPlot()
            self.heights.clearData()
            slope_label = self.slopes_plot.writeLabel(type="RMS Slopes", value=data["roundslopes"], units="urad")
            height_label = self.height_plot.writeLabel(type="RMS Heights", value=data["roundheights"], units="um")
            x_data = data["x_array"]/1000
            self.slopes_plot.updatePlotBatch(self.fittedslopes_plot, x_data, data["slopes"])
            self.height_plot.updatePlotBatch(self.heights, x_data, data["heights"])
            self.slopes_plot.setCustomLabel(slope_label)
            self.height_plot.setCustomLabel(height_label)
            self.slopes_plot.forceAutoRange()
            self.height_plot.forceAutoRange()
            #self.height_plot.updatePlot()

        if msg_type == "meas_plot_update":
            """ self.slopesarray_plot.clearData()
            self.fittedslopes_plot.clearData()
            self.heights.clearData()"""
            if (len(data["x_array"])) == 0:
                self.slopes_plot.clearPlot()
                self.height_plot.clearPlot()
                return
            x_data = data["x_array"]/1000
            self.slopes_plot.updatePlotBatch(self.slopesarray_plot,x_data, data["raw_slopes"])
            self.slopes_plot.updatePlotBatch(self.fittedslopes_plot,x_data, data["fitted_slopes"])
            self.height_plot.updatePlotBatch(self.heights, x_data, data["heights"])
            self.slopes_plot.forceAutoRange()
            self.height_plot.forceAutoRange()

            slopesarray_label = ("As-measured slopes")
            self.slopes_plot.setCustomLabel(slopesarray_label)
            """self.slopes_plot.rightViewBox.autoRange()
            self.slopes_plot.plotWidget.enableAutoRange("xy")"""
            #self.slopes_plot.updatePlotItem()

        if msg_type == "get_save_dir":
            self.measurement.get_save_directory()

        if msg_type == "end_measurement" :
            self.endmeasurement()

        if msg_type == "centroid_calc":
            self.centroid_calculation(data["image"])

        if msg_type == "meas_bwd_plot_update":
            x_bwd = data["x_bwd"] / 1000.0
            self.slopes_plot.updatePlotBatch(self.slopes_bwd_plot, x_bwd, data["fitted_bwd"])
            self.slopes_plot.forceAutoRange()


        elif msg_type == "stop_measurement":
            self.on_measurement_stopped()
        #else:
            #print(f"Unknown data type: {msg_type}")

    def endmeasurement(self):
        """
        Moved this bit in the start_measurement method.

        :return:
        self.save_data(self.myposarray, self.slopesarray, self.slopes_to_be_plotted, self.heightsarray)
        Housekeeping after each single measurement

        if self.xStartPos is not None:
            print(f"Returning the stage to the starting posisition: {self.xStartPos}")
            act_speed = self.motors.X.jogspeed
            self.motors.X.setjogspeed(25)
            self.motors.xmove.move_abs(speed="rapid", coord=float(self.xStartPos))
            print("End of Measurement!" + "\n" + f"Stage at the original position.")
            self.motors.X.setjogspeed(act_speed)"""

        self.motors.messenger.pause()
        if self.measurement_thread is not None:
            try:
                self.measurement_thread.update_signal.disconnect()
                self.measurement_thread.end_signal.disconnect()

            except (TypeError, RuntimeError):
                # Already disconnected
                pass
            self.measurement_thread.stop()
            self.measurement_thread.running = False
            self.measurement_thread = None
        self.motors.messenger.resume()
        #Reset camera to original width and height: 20260121 MA
        self.camViewer.camera.reset_sensor()
        self.clear_gui()

    def centroid_calculation(self, image):
        #print("inside centroid calculation", type(image))
        centroid = MathUtils.centroid(image)
        """self.averageX += centroid[1]  # this is the HOR vector @ Y = centroid[1], i.e. parallel to HOR axis
        self.averageY += centroid[0]  # this is the VERTICAL vector @ X = centroid[0], i.e. parallel to vertical axis"""
        #SWAPPED 20260202 due to camera rotation:
        self.averageX += centroid[0]
        self.averageY += centroid[1]
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

    def waitformoveend(self, my_time = 60.0):
        success = self.motors.xmove.wait_until_done(timeout = my_time)
        if not success:
            print("Warning: move timed out or InPos not confirmed")
            self.measurement_thread.update_signal.emit({
                "type": "Warning",
                "title": "Move Failed",
                "message": "Warning: move timed out or InPos not confirmed"
            })
        """while not self.motors.xmove.movecomplete:
            time.sleep(my_time)
            self.motors.xmove.check_in_pos()
            #QCoreApplication.processEvents()  # allows Qt signals to be processe
        time.sleep(my_time)"""

    def on_measurement_stopped(self):
        # TODO: dump all the motors positions into a file. Then set the positions after homing to those values
        old_coords_dict = self.motors.get_all_pos()
        self.motors.stopall()
        if self.measurement_thread is not None:
            try:
                self.measurement_thread.update_signal.disconnect()
                self.measurement_thread.end_signal.disconnect()

            except TypeError:
                # Already disconnected
                pass
            self.measurement_thread.stop()
            self.measurement_thread.running = False
            self.measurement_thread = None
        # print("Thread killed")
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

    def center_laser(self):
        """
        First sketch of the method: 20251111.

        This function centers the laser on the CCD, while positioned at the center of the mirror.
        The idea is to run this AFTER the user has set all the relevant measurement parameters.
        Desired centroid position on Camera if laser is @ mirror center:

        X = 2640
        Y = 2300
        remember:
        Roll controls centroid X, positive roll means DECREASING centroid X value
        Pitch controls centroid Y, positive pitch means INCREASING centroid Y value

        """
        desired_centroid = [ 2640.0, 2300] # in X and Y respectively!
        tol = 0.3 # tolerance for the comparison.
        print("Centering the laser on the mirror")
        print("Some preliminary settings first...")
        print("")
        original_laser_power = self.laser.serialmessage(isOUTPOWLEVEL)
        self.laser.serialmessage(LASPOWLEVEL + "0.002")
        original_speed = self.motors.X.getjogspeed()
        self.motors.X.setjogspeed(20)
        self.motors.xmove.move_rel(distance = self.length/2)
        self.waitformoveend()

        mov_unit = 0.0002 # based on the observation that 0.0002 deg movements means about 1 pixel variation.
        print("Starting the centering loop now...")
        while n <= 10: #let's do 10 iterations max.
            print(f"iteration nr {n}")
            print("")
            image = self.camViewer.camera.grabdata()
            if image is not None:
                meas_centroid = MathUtils.centroid(image)
                # centroid[1] this is the HOR vector @ Y = centroid[1], i.e. parallel to HOR axis
                # centroid [0] this is the VERTICAL vector @ X = centroid[0], i.e. parallel to vertical axi
            centroid = [ round(el, 1) for el in meas_centroid]
            delta = centroid - desired_centroid
            print("Delta vector (actual - desired): ", delta)

            if abs(delta) <= tol:
                break
            if n == 10:
                self.show_warning("Warning!",
                                  message = "Laser could not be centered within the allowed iterations.")
                return
            rel_move_x = - delta[0] * mov_unit
            rel_move_y = delta[1] * mov_unit
            self.motors.rollmove.move_rel(distance = rel_move_x)
            self.waitformoveend()
            self.motors.pitchmove.move_rel(distance = rel_move_y)
            self.waitformoveend()
            n += 1
        # Resetting to original state:
        self.laser.serialmessage(original_laser_power)
        self.motors.xmove.move_rel(distance = - self.length/2)
        self.motors.X.setjogspeed(original_speed)
        print("Laser correctly centered!")
        return

    def setXstartPos(self):
            self.xStartPos = self.motors.messenger.coordinates["X"]
            self.show_warning("Warning!", "Measurement starting position set!")

    def initHeightTab(self):
        self.height_plot = RealTime_plotter()
        height_layout = QtWidgets.QVBoxLayout(self.gui.height_tab)
        height_layout.addWidget(self.height_plot)
        self.gui.height_tab.setLayout(height_layout)
        self.height_plot.setLabels(bottom_label = "X position", bottom_units = "mm", left_label="Heights", left_units = "um")
        self.height_plot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.heights = MyPlot(color = 'b', width = 1,
                              symbol = "o", symbolSize = 8, symbolBrush='b', symbolPen = None,
                              name = "Height", y_axis = "left")
        self.height_plot.addPlot(self.heights)
        #print("height plot initialized")

    def initSlopesTab(self):
        self.slopes_plot = RealTime_plotter()
        slopes_layout = QtWidgets.QVBoxLayout(self.gui.Slopes_tab)
        slopes_layout.addWidget(self.slopes_plot)
        self.gui.Slopes_tab.setLayout(slopes_layout)
        self.slopes_plot.setLabels(bottom_label = "X position", bottom_units = "mm",
                                   left_label="Fitted Slope", left_units = "rad",
                                   right_label = "Raw Slope", right_units = "rad")
        self.slopes_plot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #Two-lines plotting capability.
        # Forward raw slopes (Blue)
        self.slopesarray_plot = MyPlot(color='b',
                                       width=1,
                                       symbol='o',
                                       symbolSize=8,
                                       symbolBrush="b",
                                       symbolPen='b',
                                       name="Fwd Raw",
                                       y_axis="right")
        # Backward raw slopes (Green)
        self.slopes_bwd_plot = MyPlot(color='g',
                                      width=1,
                                      symbol='o',
                                      symbolSize=6,
                                      symbolBrush="g",
                                      symbolPen='g',
                                      name="Bwd Fitted",
                                      y_axis="left")
        # Fitted / Averaged residual slope (Red)
        self.fittedslopes_plot = MyPlot(color='r',
                                        width=1,
                                        symbol='d',
                                        symbolSize=6,
                                        symbolBrush="r",
                                        symbolPen='r',
                                        name="Fitted / Residual",
                                        y_axis="left")

        self.slopes_plot.addPlot(self.slopesarray_plot)
        self.slopes_plot.addPlot(self.slopes_bwd_plot)
        self.slopes_plot.addPlot(self.fittedslopes_plot)
        #print("slopes plot initialized")

    def initCameraTab(self):
        print("Inside Init camera tab")
        print("Instantiating detector...")
        self.camViewer = CamViewer(self.detector)

        print("Done!")

        print("Adding camera to the main GUI...")

        CamTabLayout = QtWidgets.QVBoxLayout(self.gui.cam_tab)
        CamTabLayout.addWidget(self.camViewer)
        print("Done")

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
        if hasattr(self, 'shell') and self.shell and getattr(self.shell, 'alive', False):
            self.shell.close_connection()  # Close SSH connection if applicable
        if hasattr(self, 'camviewer') and self.camViewer.camera:
            self.camViewer.camera.closecam() #closes the Cam.
        event.accept()  # Allow the window to close

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MeasurementControls(None)
    window.show()
    sys.exit(app.exec_())