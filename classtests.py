"""from Communication.MCL import *
from Hardware.obis_commands import *

test = SerialConn()
print(test.is_open)

print("Using SerialConn.serialmessage")
alan2 = test.serialmessage(LASON + ' OFF')
alan3 = test.serialmessage(isLASON)
print("HIGH POW limit: ", test.serialmessage(isPOWHIGHLIM))

print(alan2, type (alan2))
print()
print(alan3, type (alan3))

print(float(alan3) -  float(alan2))

print("Using SerialConn.serialSend + SerialConn.serialread")

test.serialsend(isHSHAKE)
time.sleep(0.07)
print(test.serialread())

test.close()"""
from Communication.MCG import *
from Hardware.Motors import MotorUtil, Move, CompMotor, Motor


"""
Part one: opening the communication
"""
shell = Gantry()

shell.username =  "root"

shell.password = "deltatau"
shell.pmac_ip = "192.168.0.200"

# opening ssh channel:
shell.openssh()

print("SSH connection open: ", shell.alive)
#input("...waiting")

#initing the PMAC correctly:
#shell.send_receive("\n")
shell.pmac_init()
#  shell.pmac_init()
if shell.isinit == False:
    shell.pmac_init()

print("status of pmac initialization: ", shell.isinit)
#input("...waiting...")


#print(shell.textoutput)s
shell.set_echo()

print("setting echo on Pmac: ", shell.echo)
input("...waiting")

"""Part 2: testing the  MOTORS module"""
print("testing the MOTORS module now.")
print('\n')

print("Initing MotorUtil object util = MotorUtil(shell)...")
print("\n")
util = MotorUtil(shell)
mylist = util.motors()
alan = len(mylist)
try:
    alan =0
except ValueError:
    print("motor's list not compiled!")
else:
    print("Motor's list successfully inited!")
    print(mylist)
print('\n')
input("...waiting...")
print("\n")
print("Initing Motors objects ...")
print("\n")
motor1 = Motor(connection = shell, motorID=mylist[0][1], cs=mylist[0][0])
motor2 = Motor(connection = shell, motorID=mylist[1][1], cs=mylist[1][0])
motor3 = Motor(connection = shell, motorID=mylist[2][1], cs=mylist[2][0])
yaw = Motor(connection = shell, motorID=mylist[3][1], cs=mylist[3][0])
X = Motor(connection = shell, motorID=mylist[4][1], cs=mylist[4][0])
Y = Motor(connection = shell, motorID=mylist[5][1], cs=mylist[5][0])

"""
Here the composite motors, as objects of class CompMotor
"""
Z = CompMotor(connection = shell, pmac_name="Z", cs=1)
pitch = CompMotor(connection = shell, pmac_name="B", cs=1)
roll = CompMotor(connection = shell, pmac_name="A", cs=1)
print("Motors inited ...")
print("\n")
print("Initializing Move objects for relevant motors: ")
print("\n")

yawmove = Move( connection = shell, motor = yaw, util = util )
xmove = Move( connection = shell, motor = X, util = util )
ymove = Move( connection = shell, motor = Y, util = util )
zmove = Move( connection = shell, motor = Z, util = util )
pitchmove = Move( connection = shell, motor = pitch, util = util )
rollmove = Move(connection = shell, motor = roll, util = util)

print("Move objects succesffully inited! ")
print("all yours\n")

def initmotors(motorlist):
    """
    This is Elettra-specific.
    CS 1: motor 1, 2 and 3 are inited as instances of Motor class as 1, 2 and 3.

    :param motorlist: a list containing all the motors of the system.
    :return:
    """
    motornr = len(motorlist)

    """
    Here the single motors, as objects of class Motor: 
    """
    motor1 = Motor(connection = shell, motorID =mylist[0][1], cs =mylist[0][0])
    motor2 = Motor(connection = shell, motorID =mylist[1][1], cs =mylist[1][0])
    motor3 = Motor(connection =shell, motorID=mylist[2][1], cs=mylist[2][0])
    yaw = Motor(connection =shell, motorID =mylist[3][1], cs =mylist[3][0])
    X = Motor(connection =shell, motorID =mylist[4][1], cs =mylist[4][0])
    Y = Motor(connection =shell, motorID =mylist[5][1], cs =mylist[5][0])

    """
    Here the composite motors, as objects of class CompMotor
    """
    Z = CompMotor(connection =shell, pmac_name= "Z", cs = 1)
    pitch = CompMotor(connection =shell, pmac_name = "B", cs = 1)
    roll = CompMotor(connection =shell, pmac_name = "A", cs = 1)

    return(motor1, motor2, motor3, yaw, X, Y, Z, pitch, roll)


