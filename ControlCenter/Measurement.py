import datetime
from Hardware import Source, Motors, Detector
from Communication import MCG, MCL
from ControlCenter import Control_Utilities as cu
import scipy

TODAY = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# Initing the objects for measurements:

# SSH shell to the PMAC
factory = cu.Utilities()
conn1 = factory.create("shell", pmac_ip= "192.168.0.200", username = "root", password = "deltatau")
conn1.openssh()

#Laser:
laser = factory.create("laser")

#motor utilities, instantiating all the motors and move objects

util = factory.create("util", connection = conn1)
motorlist = util.motors()

motor1, motor2, motor3, yaw, X, Y, Z, pitch, roll, motordict = util.init_motors(motorlist, conn1)

yawmove, xmove, ymove, zmove, pitchmove, rollmove = factory.init_moves(motordict, conn1, util)

#camera:
camera = factory.create("camera")
camera.opencam()


# Now the fun begins:

class Measurement():
    def __init__(self, nr_of_points = 10, length = 1, \
                 xmotor, xmove,\
                 ymotor, ymove,  \
                 zmotor, zmove, \
                 pitch, pitchmove,  \
                 roll, rollmove,  \
                 yaw, yawmove, \
                 camera):
        self.nr_of_points = nr_of_points
        self.length = length  # length of measurement, units in m. Must be converted to µm, as that's the unit of X.
        self.xmotor = xmotor
        self.xmove = xmove

        self.ymotor = ymotor
        self.ymove = ymove
        self.zmotor = zmotor
        self.zmove = zmove
        self.pitch = pitch
        self.pitchmove = pitchmove
        self.roll = roll
        self.rollmove = rollmove
        self.yaw = yaw
        self.yawmove = yawmove

        self.camera = camera

        self.x_start_pos = self.xmotor.get_real_pos()
        self.y_start_pos = self.ymotor.get_real_pos()
        self.z_start_pos = self.zmotor.get_real_pos()
        self.pitch_start_pos = self.pitch.get_real_pos()
        self.roll_start_post = self.roll.get_real_pos()
        self.yaw_start_pos = self.yaw.get_real_pos()
        self.images = []
        self.sampling = self.length / self.nr_of_points

    def measure(self):
        """
        this assumes the X stage is already in its correct starting position
        :return:
        """
        for i in range(self.nr_of_points):
            image = self.camera.grabdata()  # already grabbing 10 images by default

            #TODO: finish writing the measure method. Check camera_tests.py et similia 20240704



