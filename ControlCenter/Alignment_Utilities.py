from Graphics.Base_Classes_graphics.BaseClasses import *
from ControlCenter.Measurement import *
from ControlCenter.MathUtils import *
"""
This is coded as I go, the idea is as follows:
Given the mirror position on the stage
the mirror size in X (L, long axis, mm)
the mirror size in Y (W, short axis, mm)

The code should
1) find a spot on the CMOS (<- need to write a routine for this)
2) Scan the Y axis at one end of the mirror (say X1 - X2  = 0.8 * L)
        - Find the Y1 position where the spot is 1/2 of its max value
        - Find the Y2 position where the spot is 1/2 of its max value
    This is one end. 
3) Scan the Y axis at the other end of the mirror (say X2)
        - Find the Y3 position where the spot is 1/2 of its max value
        - Find the Y4 position where the spot is 1/2 of its max value
4) calculate the tangent of the yaw angle as :
        tan(yaw_angle) = (Y3 - Y1) / (X2 - X1)
5) check that is it the same as:
        tan(yaw_angle) = (Y4 - Y2) / (X2 - X1)
6) rotate the stage by yaw_angle (<- need to check the sign on the stage)

7) check at X1 and X2 that Y1,3 and Y2,4 are the same.

8) set the center mirror @ Ycenter = (Y2+Y1)/2 in Y.  (<calc done)

9) move to X1, then move by -0.2*L in X to find the edge of the mirror

10) note the X position where the spot is 1/2 of its max value Xmin

11) move to X2, then move by 0.2*L in X to find the edge of the mirror

12) note the X position where the spot is 1/2 of its max value as Xmax

13) prompt the user with the calculated Lcalc = (Xmax - Xmin)

14) set the center mirror position in X @ (Xmax + Xmin)/2 (<done)

15) align pitch and roll so that the centroid of the spot is @ 2640 2300

16) move to Xstart(Xmin+5 mm), calculate Xend as (Xmax-5 mm), set L as Xmax - Xmin

17) Prompt the user with the Length of measurement.

"""

class Aligner():
    def __init__(self, motors = None, detector = None, laser = None):

        # here below the hardware resources needed, shich should be passeed by the caller:
        self.motors = MotorControls()
        self.detector = DetectorControls()
        self.laser = Laser()

        #Flags:
        self.spot_found = False
        self.center_set = False
        self.yaw_found = False

        # Aligner properties:
        self.mirrorsizeX = 0.0
        self.mirrorsizeY = 0.0
        self.roughXcenter = 0.0  # this has to be set in the GUI by the user
        self.roughYcenter = 0.0 # this has to be set in the GUI by the user.

        #Geometrical properties of the aligner:
        self.X1 = 0.0
        self.Y1 = 0.0
        self.X2 = 0.0
        self.Y2 = 0.0
        self.Y3 = 0.0
        self.Y4 = 0.0

        #Search start parameters:
        self.Ystart_bottom= 0.0
        self.Ystart_top = 0.0


        #Measurement properties:
        self.Xcenter = 0.0
        self.Ycenter = 0.0
        self.measurement_length = 0.0
        self.intensity_start = 0.0  #Intensity of the spot at the starting point.

        #Calculated properties:
        self.Xmin = 0.0
        self.Xmax = 0.0
        self.Xstart = 0.0
        self.Xend = 0.0
        self.yaw_angle = 0.0 # This must be in degrees for the stage!!!

    def set_center(self, to_be_centered, coord1, coord2):
        """
        exampple usage:

        self.setCenter(self.Xcenter, self.X1, self.X2)

        :param 2b_centered: self.Xcenter or self.Ycenter, a class property
        :param coord1: X1 or Y1
        :param coord2: X2 or Y2
        :return: no return, the center is set in 2b_centered.
        """
        to_be_centered = (coord1+coord2)/2

    def set_start_values (self):
        """

        :return:
        """
        self.X1 = self.roughXcenter - 0.4 * self.mirrorsizeX # closer to laser head
        self.X2 = self.roughXcenter + 0.4 * self.mirrorsizeX
        self.Ystart_bottom = self.roughYcenter - 0.4 * self.mirrorsizeY
        self.Ystart_top = self.roughYcenter + 0.4 * self.mirrorsizeY

    def on_set_rough_center_clicked(self):
        """
        Get the user to manually position the laser at the center of the mirror and hit the  set-the-rough-center button
        :return:
        """

        self.roughXcenter = self.motors.messenger.coordinates["X"]
        self.roughYcenter = self.motors.messenger.coordinates["Y"]

    def find_spot(self):
        """
        this will set sef.spot_found to True if the spot is found.
        :return:
        """
        pass
    def move_rel_and_find(self, axis, distance):
        if axis == "X":
            self.motors.xmove.move_rel(distance, speed = "rapid")
        elif axis == "Y":
            self.motors.ymove.move_rel(distance, speed = "rapid")
        self.find_spot()

    def find_Y_limits(self, startXposition, maxtries = 10):
        """
        TODO: Check movements of the Y axis, there is a minus sign that needs to be
        TODO: added to the  searching method!!!
        TODO: implement the find_spot method!!!!

        :param startXposition: starting X position, should be either self.X1 or self.X2
        :return:
        """
        # Compute and store the starting spot intensity:
        self.intensity_start = Measurement.compute_spot_intensity()

        #move the stage to starting position

        if self.motors.messenger.coordinates["X"] - startXposition  >10:# 10 microns difference is the key for moving
            self.motors.xmove.move_abs(self.motors.messenger.coordinates["X"], speed = "rapid")

        #move the stage to one of the Y'start positions
        self.motors.ymove.move_abs(self.Ystart_bottom, speed = "rapid")

        #scan the Y axis at the bottom

        self.find_spot() # this should find the spot and prep the following loop
        distance = 1000  # start with 1 mm moves, let's give us 10 tries for starters:

        if self.spot_found == False:
            warning = MyWarningBox(title = "No spot!",
                                     message ="No spot found at the bottom, check the mirror position and try again")
            warning.show_warning()
            return # this bring the control back.
        i = 0 # start a counter
        while self.spot_found and i < maxtries: # if there's a spot, there's a mirror:
            self.move_rel_and_find(axis="Y", distance = distance)
            i = i + 1

        #Now we either have found the mirror's edge, or a counter thats at the limit of our desired range.
        if i == maxtries:
            mywarning = MyWarningBox(title = "No spot found!",
                                     message = "No spot found in search area!")
            mywarning.show_warning()
            return # this bring the control back.
        else: # we found the mirror's edge, now we have to find the position where the spot is 1/2 of its max value
            distance = -0.5 * distance # we got a little closer. since distance was positive, now we add a minus:
            for i in range (4):
                self.move_rel_and_find(axis="Y", distance = distance)
                if self.spot_found:
                    newInt = Measurement.compute_spot_intensity()
                    if MathUtils.compare_within(newInt, 0.5*self.intensity_start , 0.1):
                        # this is the bingo condition: I have found the Y limit at this edge of the mirror
                        self.Y1 = self.motors.messenger.coordinates ["Y"]
                        return
                    else:
                        pass




