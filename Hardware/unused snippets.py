def move_rel_one_axis(self, axis, speed, distance="0"):
    """
            See motor definition above!!!
            This method outputs a command for moving ONE AXIS only. It is possible to move more than one axis i.e.
            &1 cpx rapid abs A-1 B15 Z13400  but this will be implemented later
            This is an "inc" move, i.e. relative.

            :param axis: axis for motion
            :param speed: linear (i.e. slow, pmac default) or rapid.
            :param distance: distance of motion
            :return: a string containing the move, to be passed to a shell for execution by the PPMAC
            """
    move = f'&{str(self.cs)} cpx {str(speed)} inc {self.axis_conversion(axis)}{distance}\n'

    """move += str(self.cs)
    move += "cpx "
    move += str(speed)
    move += " inc "
    move += " "
    move += self.axis_conversion(axis)
    move += " "
    move += str(distance)
    move += "\n"
    # The next lines are for debugging
    # print(command)
    # output = str("Move: " + command + " sent as requested")"""
    return (move)


def move_abs_one_axis(self, axis, speed, coordinate="0"):
    """
            See motor definition above!!!
            This method outputs a command for moving ONE AXIS only. It is possible to move more than one axis i.e.
            &1 cpx rapid abs A-1 B15 Z13400  but this will be implemented later
            This is an "inc" move, i.e. relative.

            :param axis: axis for motion
            :param speed: linear (i.e. slow, pmac default) or rapid.
            :param distance: distance of motion
            :return: a string containing the move, to be passed to a shell for execution by the PPMAC
            """
    move = f'&{str(self.cs)} cpx {str(speed)} abs  {self.axis_conversion(axis)}{coordinate}\n'

    return (move)

@classmethod
    def sr_check(cls, axis):
        """
        This checks the axis (X, Y, Z, Roll, etc) the user wants to move, and detects the System of Reference for the move
        according to the QSYS convention specified above.

        :param axis: a string specifying the axis to be moved.
        :param cls: the class itself
        :return: an int value for the system of reference of the selected axis.
        """
        axis = axis.lower()
        if axis == "x" or axis == "y":
            sr = str(3)
        elif axis == "pitch" or axis == "roll" or axis == "z":
            sr = str(1)
        elif axis  == "rot" or axis == "rotation":
            sr = str(2)

        return (sr)

    @classmethod
    def speed_check(cls, speed):
        """
        this should output as default a linear, i.e.  a slow movement

        :param cls: the class itself
        :param speed: a string, either rapid or linear
        :return: a string useful for composing a move
        """
        if speed in ["Rapid", "rapid", "fast", "Fast"]:
            out = "rapid"
        else:
            out = "linear"
        return out

    @classmethod
    def mode_check(cls, mode):
        """
        This should output inc as default, i.e. a relative move, avoiding the user sending a motor to the moon.
        :param mode: a string, either abs or inc
        :return: a string useful for composing a move
        """
        if mode in ["Absolute", "ABS", "absolute", "Abs", "abs"]:
            out = "abs"
        else:
            out = "inc"
        return out

    @classmethod
    def axis_conversion(cls, axis):
        """
        Converts axis as input by user back into Pmac-understandable format


        :param cls: the class itself
        :param axis: X, Y, Z, pitch, roll, rot
        :return: X,Y, Z, A, B, C depending on the user choice
        """
        axis = str(axis).lower()
        if axis =="x":
            ret = "X"
        elif axis == "y":
            ret = "Y"
        elif axis == "z":
            ret = "Z"
        elif axis == "pitch":
            ret = "B"
        elif axis == "roll":
            ret = "A"
        elif axis == "rot" or axis == "rotation" or axis == "yaw":
            ret = "C"
        return (ret)


def centerLaser(self):
    """
    First sketch of the method: 20251111.

    This function centers the laser on the mirror.
    The idea is to run this AFTER the user has set all the relevant measurement parameters.
    Desired centroid position on Camera if laser is @ mirror center:

    X = 2640
    Y = 2300
    remember:
    Roll controls centroid X
    Pitch controls centroid Y

    """
    desired_centroid_x = 2640
    desired_centroid_y = 2300
    original_laser_power = self.laser.serialmessage(isOUTPOWLEVEL)
    print("Centering the laser on the mirror...")
    self.laser.serialmessage(LASPOWLEVEL + "0.002")
    original_speed = self.motors.X.getjogspeed()

    self.motors.X.setjogspeed(20)
    self.motors.xmove.move_rel(distance=self.length / 2)
    self.waitformoveend()

    image = self.camViewer.camera.grabdata()
    if image is not None:
        centroid = self.centroid_calculation(image)
        """centerX += round(centroid[1], 0)  # this is the HOR vector @ Y = centroid[1], i.e. parallel to HOR axis
        centerY += round(centroid[0],0)  # this is the VERTICAL vector @ X = centroid[0], i.e. parallel to vertical axi"""
    while centroid != [desired_centroid_x, desired_centroid_y]:
        self.centering_loop(centroid, increment=0.0001)
        image = self.camViewer.camera.grabdata()
        if image is not None:
            centroid = self.centroid_calculation(image)

    #

    # Resetting to original state:
    self.laser.serialmessage(original_laser_power)
    self.motors.xmove.move_rel(distance=- self.length / 2)
    self.motors.X.setjogspeed(original_speed)
    print("Laser correctly centered!")


def centering_loop(self, actual, increment=0.0001):
    """

    :param actual: centroid as a list!
    :param increment: angular increment for motion
    :return:
    """
    if actual[0] != ZERO_X:
        move1 = "roll"
    elif actual[1] != ZERO_Y:
        move2 = "pitch"

