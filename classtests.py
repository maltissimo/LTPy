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
from Hardware.Motors import *


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
input("...waiting")

#initing the PMAC correctly:
#shell.send_receive("\n")
shell.pmac_init()
#  shell.pmac_init()
if shell.isinit == False:
    shell.pmac_init()

print("status of pmac initialization: ", shell.isinit)
input("...waiting...")


#print(shell.textoutput)
shell.set_echo()

print("setting echo: ", shell.echo)
input("...waiting")

"""Part 2: testing the  MOTORS module"""
print("testing the MOTORS module now.")
print('\n')

print("Initing MotorUtil object util = MotorUtil(shell)...")
print("\n")
util = MotorUtil(shell)
motorlist = util.motor()

print(motorList)
input("...waiting")



