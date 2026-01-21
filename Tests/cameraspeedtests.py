from Hardware.Detector import *
import time
cam = Camera()
nr_of_grabs = 1000
start = time.time()
for _ in range (nr_of_grabs):
    cam.grabdata()
end = time.time()
cam.closecam()
print(f"time for {nr_of_grabs} grabs : {end - start} seconds")