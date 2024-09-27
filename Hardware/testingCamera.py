from pypylon import pylon as py
from matplotlib import pyplot as plt

camera = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())

camera.Open()
camera.UserSetSelector = "Default"
camera.UserSetLoad.Execute()

camera.ExposureTime = 20
res = camera.GrabOne(100)
camera.StopGrabbing()
img = res.Array
plt.imshow(img)

plt.ion()
fig, ax = plt.subplots()

print("press CTRL+C to quit")

camera.StopGrabbing()
camera.StartGrabbing(py.GrabStrategy_LatestImageOnly)

try:
    while camera.IsGrabbing():
        camera.ExposureTime = 15
        res = camera.RetrieveResult(5000, py.TimeoutHandling_ThrowException)
        """ with camera.RetrieveResult(100) as res:"""
        if res.GrabSucceeded():
            image = res.Array
            ax.imshow( image)
            plt.draw()
            plt.pause(0.01)
        res.Release()

except KeyboardInterrupt:
    print("exiting")
camera.StopGrabbing()
plt.ioff()
