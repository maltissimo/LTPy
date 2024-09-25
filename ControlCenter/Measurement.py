import datetime

from PyQt5 import QtWidgets
from scipy import ndimage

from ControlCenter import Control_Utilities as cu
from Graphics.Base_Classes_graphics import RT_Dataplot, Measurements_GUI,
from Graphics.CameraViewer import *

TODAY = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# Initing the objects for measurements:

# SSH shell to the PMAC
factory = cu.Utilities()
conn1 = factory.create("shell", pmac_ip="192.168.0.200", username="root", password="deltatau")
conn1.openssh()

#Laser:
laser = factory.create("laser")

#motor utilities, instantiating all the motors and move objects

util = factory.create("util", connection = conn1)
motorlist = util.motors()

motor1, motor2, motor3, yaw, X, Y, Z, pitch, roll, motordict = util.init_motors(motorlist, conn1)

yawmove, xmove, ymove, zmove, pitchmove, rollmove = factory.init_moves(motordict, conn1, util)

# camera:
camera = factory.create("camera")
camera.opencam()


class MeasurementControls(QtWidgets.QApplication):
    """

    this is largely for dealing with the graphics and connecting all the bits to the right places.

    """

    def __init__(self):
        super().__init__()

        # Create an instance of the Measurement_GUI class:
        self.gui = Measurements_GUI()
        self.gui.setupUI(self)

        self.xStartPos = X.get_real_pos()

        self.initHeightTab()
        self.initSlopesTab()
        self.initCameraTab() = CamViewer()

        self.gui.connect.startButton(self.startMeasurement)
        self.gui.connect.stopButton(self.stopMeasurement)

        self.gui.connect.xStartPos(self.setXstartPos)

    def startMeasurement(self):
        pass

    def stopMeasurement(self):
        pass

    def setXstartPos(self):
        self.xStartPos = X.get_real_pos()

    def initHeightTab(self):
        self.gui.setTabText(0, "Height Measurements")

        self.RTplot = RT_Dataplot(self)
        self.RTplot.setLabels(left_label="Heights", left_units="µm")
        self.RTplot.setLabels(bottom_label="X position", bottom_units="mm")
        self.graphLayout.addWidget(self.RTplot)

        self.HeightTabLayout = QtWidgets.QVBoxLayout(self.gui.height_tab)
        self.HeightTabLayout.addWidget(self.RTplot)

    def initSlopesTab(self):
        self.gui.setTabText(1, "Slope Measurements")

        self.RTplot = RT_Dataplot(self)
        self.RTplot.setLabels(left_label="Slopes", left_units="µrad")
        self.RTplot.setLabels(bottom_label="X position", bottom_units="mm")
        self.graphLayout.addWidget(self.RTplot)

        self.SlopesTabLayout = QtWidgets.QVBoxLayout(self.gui.slopes_tab)
        self.SlopesTabLayout.addWidget(self.RTplot)

    def initCameraTab(self):
        self.gui.setTabText(2, "Camera")

        self.CamTabLayout = QtWidgets.QVBoxLayout(self.gui.cam_tab)
        self.CamTabLayout.addWidget(camera)


# Now the fun begins:

class Measurement():
    def __init__(self, nr_of_points=10, length=1,
                 xmotor, xmove,
                 ymotor, ymove,
                 zmotor, zmove,
                 pitch, pitchmove,
                 roll, rollmove,
                 yaw, yawmove,
                 camera):

        self.nr_of_points = nr_of_points
        self.length = length  # length of measurement, units in m. Must be converted to µm, as that's the unit of X.
        self.xmotor = X
        self.xmove = xmove

        self.ymotor = Y
        self.ymove = ymove
        self.zmotor = Z
        self.zmove = zmove
        self.pitch = pitch
        self.pitchmove = pitchmove
        self.roll = roll
        self.rollmove = rollmove
        self.yaw = yaw
        self.yawmove = yawmove

        self.camera = camera

        self.x_start_pos = self.X.get_real_pos()
        self.y_start_pos = self.Y.get_real_pos()
        self.z_start_pos = self.Z.get_real_pos()
        self.pitch_start_pos = self.pitch.get_real_pos()
        self.roll_start_post = self.roll.get_real_pos()
        self.yaw_start_pos = self.yaw.get_real_pos()
        self.images = []
        self.step = self.length / self.nr_of_points
        self.results = ""

    def measure(self):
        """
        this assumes the X stage is already in its correct starting position
        :return:
        """
        # preparing the results header

        self.results += "date of measurement: " + TODAY + "\n"
        self.results += "\t" + "X" + "\t" + "Y" + "\t" + "Z" + "\t" + "P" + "\t" + "R" + "\t" + "Y"+ "\t" + "Centroid" + "\n"
        self.results += "\n"

        for i in range(self.nr_of_points):
            image = self.camera.grabdata()  # already grabbing 10 images by default
            step_result = self.centroid(image) #this is an array, with 2 coordinates of the centroid.
            #Result for this position:
            self.results += self.get_all_motor_pos()
            self.results += step_result
            self.xmove.move_rel(distance = self.step)
    def centroid(self, ndarray):
        centroid = ndimage.center_of_mass(ndarray)
        return(centroid)

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
        return(pos_all)

    def save_data(self):
        filename = "data of " + TODAY ".txt"
        with open (filename, "w", encoding = "ASCII") as f:
            f.write(self.results)

        print("Data saved into: " + filename )



#TODO: start working on a GUI. See Dynamic Graph in the Gantrycomms directory for starters
#TODO: implement a checking method in Control Utilities that works before each measurement is performed
# and checks whether all the subsystems are operational.



