import threading


def synchronized_method(method):
    outer_lock = threading.Lock()
    lock_name = "__" + method.__name__ + "__lock" + "__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name): setattr(self, lock_name, threading.Lock())
            lock = getattra(self, lock_name)
            with lock: return method(self, *args, **kws)

    return sync_method()


from PyQt5.QtCore import QObject, pyqtSignal


class WorkerThread(QObject):
    """Signals definition:"""

    update_signal = pyqtSignal(str)  # signal to send updates to the main thread
    begin_signal = pyqtSignal()  # signal to send the start of sub-thread to the main thread
    end_signal = pyqtSignal(str)  # signal to send the end of sub-thread to the main thread

    """Init method for the WorkerThread Object"""

    def __init__(self, task_function, *args, **kwargs):
        super().__init__()
        self.task_function = task_function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.begin_signal.emit()
        try:
            self.update_signal.emit("Thread started")
            result = self.task_function(*self.args, **self.kwargs)
        self.update_signal.emit("Thread finished")

        finally:
        self.end_signal.emit(result)
