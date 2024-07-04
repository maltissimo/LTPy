from Hardware import Source, Motors#, Detector
from Communication import MCG, MCL

class Utilities():
    def create(self, my_object, **kwargs):
        if my_object == "shell":
            shell = MCG.Gantry(
                pmac_ip=kwargs.get("pmac_ip"),
                username=kwargs.get("username"),
                password=kwargs.get("password"),
                alive=kwargs.get("alive", False),
                nbytes=kwargs.get("nbytes", 1024),
                echo=kwargs.get("echo", None),
                isinit=kwargs.get("isinit", False)
            )
            return shell

        elif my_object == "util":
            util = Motors.MotorUtil(
                connection = kwargs.get(Pmac_connection)
            )
            return util

        elif my_object == "laser":
            laser = Source.Laser()
            return(laser)

        elif my_object == "camera":
            camera = Detector.Camera()
            return(camera)

        else:
            raise ValueError("Unknown object type!")

    def checklaser(self, laser):
        pass

    def init_motors(self, motorlist, shell):
        """
           This is Elettra-specific.
           CS 1: motor 1, 2 and 3 are inited as instances of Motor class as 1, 2 and 3.

           :param motorlist: a list containing all the motors of the system.
           param shell: an active shell to the PMAC.
           :return: initialized objects of class Motors.Motor and class Motors.CompMotor
           """

        alan = len(motorlist)
        try:
            alan = 0
        except ValueError:
            print("motor's list not compiled!")
        else:
            print("Motor's list successfully inited!")
            print(motorlist)
        motor1 = Motors.Motor(connection=shell, motorID=motorlist[0][1], cs=motorlist[0][0])
        motor2 = Motors.Motor(connection=shell, motorID=motorlist[1][1], cs=motorlist[1][0])
        motor3 = Motors.Motor(connection=shell, motorID=motorlist[2][1], cs=motorlist[2][0])
        yaw = Motors.Motor(connection=shell, motorID=motorlist[3][1], cs=motorlist[3][0])
        X = Motors.Motor(connection=shell, motorID=motorlist[4][1], cs=motorlist[4][0])
        Y = Motors.Motor(connection=shell, motorID=motorlist[5][1], cs=motorlist[5][0])

        """
        Here the composite motors, as objects of class CompMotor
        """
        Z = Motors.CompMotor(connection=shell, pmac_name="Z", cs=1)
        pitch = Motors.CompMotor(connection=shell, pmac_name="B", cs=1)
        roll = Motors.CompMotor(connection=shell, pmac_name="A", cs=1)
        motordict = {
                1: "motor1",
                2: "motor2",
                3: "motor3",
                4: "X",
                5: "Y",
                6: "Z",
                7: "pitch",
                8: "roll",
                9: "yaw"
            }

        return (motor1, motor2, motor3, yaw, X, Y, Z, pitch, roll, motordict)

    def init_moves(self, motordict, shell, util):
        yawmove = Move(connection=shell, motor=motordict[9], util=util)
        xmove = Move(connection=shell, motor=motordict[4], util=util)
        ymove = Move(connection=shell, motor=motordict[5], util=util)
        zmove = Move(connection=shell, motor=motordict[6], util=util)
        pitchmove = Move(connection=shell, motor=motordict[7], util=util)
        rollmove = Move(connection=shell, motor=motordict[8], util=util)

        return(yawmove, xmove, ymove, zmove, pitchmove, rollmove)





