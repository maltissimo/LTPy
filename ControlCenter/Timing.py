from PyQt5.QtCore import QObject, QTimer

class myTimer(QObject):
    def __init__(self, interval=50, single_shot=False, name="Unnamed timer", callback=None):
        super().__init__()
        self.timer = QTimer(self)
        self.interval = interval
        self.timer.setInterval(interval)  # set at 50 ms by default must be overridden in case.
        self.timer.setSingleShot(single_shot)
        if callback:
            self.timer.timeout.connect(callback)
        self.name = name
        # self.callback

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def is_active(self):
        return(self.timer.isActive())

    def setInterval(self, interval):
        self.timer.setInterval(interval)

    def set_single_shot(self, single_shot):
        self.timer.setSingleShot(single_shot)

    def connect_callback(self, callback):
        self.timer.timeout.connect(callback)

    def disconnect_callback(self, callback):
        self.timer.timeout.disconnect(callback)
