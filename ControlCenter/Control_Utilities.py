from Hardware import Source, Motors #, Detector
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
                connection = kwargs.get("connection")
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

    def init_motors(self, **kwargs):

        if kwargs.get("motorID"):

            motor = Motors.motor(
                connection = kwargs.get("connection"),
                motorID = kwargs.get("motorID"),
                cs = kwargs.get("cs")
            )
        else:
            motor = Motors.CompMotor(
                connection = kwargs.get("connection"),
                pmac_name = kwargs.get("pmac_name"),
                cs = kwargs.get("cs")
            )
        return motor

    def init_moves(self, **kwargs, motor):
        move = Move(connection=kwargs.get("connection"), motor=motor, util=util)
        """xmove = Move(connection=shell, motor=motordict[4], util=util)
        ymove = Move(connection=shell, motor=motordict[5], util=util)
        zmove = Move(connection=shell, motor=motordict[6], util=util)
        pitchmove = Move(connection=shell, motor=motordict[7], util=util)
        rollmove = Move(connection=shell, motor=motordict[8], util=util)

        return(yawmove, xmove, ymove, zmove, pitchmove, rollmove)"""
        return move





