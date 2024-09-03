this is from Graphics.Base_Classes_graphics.Motors_GUI

""" mylist = self.util.motors()
       alan = len(mylist)

       try:
           self.motor1.connection = self.shell
           self.motor1.motorID  = mylist[0][1]
           self.motor1.cs = mylist[0][0]

           self.motor2.connection = self.shell
           self.motor2.motorID = mylist[1][1]
           self.motor2.cs = mylist[1][0]

           self.motor3.connection = self.shell
           self.motor3.motorID = mylist[2][1]
           self.motor3.cs = mylise[2][0]

           self.X.connection = self.shell
           self.X.motorID = mylist[4][1]
           self.X.cs = mylist [4][0]

           self.Y.connection = self.shell
           self.Y.motorID = mylist[5][1]
           self.Y.cs = mylist[5][0]

           self.yaw.connection = self.shell
           self.yaw.motorID = mylist [3][1]
           self.yaw.cs = mylist [3][0]

           self.Z.connection = self.shell
           self.Z.pmac_name = "Z"
           self.Z.cs = 1

           self.pitch.connection = self.shell
           self.pitch.pmac_name = "B"
           self.pitch.cs = 1

           self.roll.connection = self.shell
           self.roll.pmac_name = "A"
           self.roll.cs = 1"""

""" self.xmove.connection = self.shell
           self.xmove.motor = self.X
           self.move.util = self.util

           self.ymove.connection = self.shell
           self.ymove.motor = self.Y
           self.ymove.util = self.util

           self.zmove.connection = self.shell
           self.zmove.motor = self.Z
           self.zmove.util = util

           self.pitchmove.connection = self.shell
           self.pitchmove.motor = self.pitch
           self.pitchmove.util = self.util

           self.rollmove.connection = self.shell
           self.rollmove.motor = self.roll
           self.rollmove.util = self.util

           self.yawmove.connection = self.shell
           self.yawmove.motor = self.yaw
           self.yawmove.util = self.util"""

this is from Control_Utilities.py:
"""alan = len(motorlist)
  try:
      alan == 0
  except ValueError:
      print("motor's list not compiled!")
  else:
      print("Motor's list successfully inited!")
      print(motorlist)
  motor1 = Motors.Motor(connection=shell, motorID=1, cs=1)
  motor2 = Motors.Motor(connection=shell, motorID=2, cs=1)
  motor3 = Motors.Motor(connection=shell, motorID=3, cs=1)
  yaw = Motors.Motor(connection=shell, motorID=4, cs=2)
  X = Motors.Motor(connection=shell, motorID=5, cs=3)
  Y = Motors.Motor(connection=shell, motorID=6, cs=3)


  Here the composite motors, as objects of class CompMotor

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
  return (motor1, motor2, motor3, yaw, X, Y, Z, pitch, roll, motordict)"""