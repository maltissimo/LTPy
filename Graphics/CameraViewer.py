from Hardware.Detector import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class CamViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.camera = Camera()
        self.timer = QTimer(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pylon Camera Viewer")

        self.canvas = FigureCanvas((plt.Figure()))
        self.start_grabbing = QPushButton("Grab!")
        self.stop_grabbing = QPushButton("Stop grabbing!")

        self.start_grabbing.clicked.connect(self.start_grab)
        self.stop_grabbing.clicked.connect(self.stop_grab)


        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.start_grabbing)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
        self.show()

    def start_grab(self):
        self.timer.timeout.connect(self.grab_data)
        self.timer.start(200) # update every 200 ms

    def stop_grab(self):
        self.timer.stop()

    def grab_data(self):
        data = self.camera.grabdata() # this should already be a np object.
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.imshow(data)
        self.canvas(draw)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CameraViewer()
    sys.exit(app.exec_())


