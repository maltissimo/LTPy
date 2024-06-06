from Communication.MCL import *
from Hardware.obis_commands import *

test = SerialConn()
print(test.is_open)

print("Using SerialConn.serialmessage")
alan2 = test.serialmessage(LASON + ' OFF')
alan3 = test.serialmessage(isLASON)
"""print("HIGH POW limit: ", test.serialmessage(isPOWHIGHLIM))"""

print(alan2, type (alan2))
print()
print(alan3, type (alan3))

"""print(float(alan3) -  float(alan2))
"""
"""
print("Using SerialConn.serialSend + SerialConn.serialread")

test.serialsend(isHSHAKE)
time.sleep(0.07)
print(test.serialread())
"""
test.close()