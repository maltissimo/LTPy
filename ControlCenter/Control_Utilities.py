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

    @staticmethod
    def motors_init( **kwargs):

        if kwargs.get("motorID"):

            motor = Motors.Motor(
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

    @staticmethod
    def init_moves(self, motor, **kwargs):

        move = Motors.Move(connection=kwargs.get("connection"), motor=motor, util=util)

        return move


