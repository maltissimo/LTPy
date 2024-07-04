from Hardware import Source, Detector, Motors
from Communication import MCG

class Utilities():
    def create(self, my_object, **kwargs):
        if my_object == "shell":
            shell = MCG.Gantry()
            return shell(
                pmac_ip = kwargs.get("pmac_ip"),
                username = kwargs.get("username"),
                password = kwargs.get("password"),
                alive = kwargs.get("alive", False),
                nbytes = kwargs.get("nbytes", 1024),
                echo = kwargs.get("echo", None),
                isinit = kwargs.get("isinit", False)
            )

        elif my_object == "util":
            util = Motors.MotorUtil(shell)
            if shell is None:
                raise ValueError ("Shell object not correctly initialized!")
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


