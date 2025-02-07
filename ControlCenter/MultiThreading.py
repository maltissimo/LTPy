import threading


def synchronized_method(method):
    outer_lock = threading.Lock()
    lock_name = "__" + method.__name__ + "__lock" + "__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name): setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock: return method(self, *args, **kws)

    return sync_method


from PyQt5.QtCore import QThread, pyqtSignal
import time

class WorkerThread(QThread):
    update_signal = pyqtSignal(object) # signal to send updates to the main thread
    begin_signal = pyqtSignal()     # signal to send begin work to the main thread
    end_signal = pyqtSignal()    # signal to send end work to the main thread
    error_signal = pyqtSignal(str) # in case there some mishap

    def __init__(self, task, *args, **kwargs):
        """
        Initialize the worker thread
        :param task: the callable (function or method) to run in the task
        :param args: positional arguments for the task
        :param kwargs: keyword arguments for the task
        """
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.running = True


    def run(self):
        self.begin_signal.emit()
        try:
            while self.running:
                self.task(*self.args, **self.kwargs)  # Call the task
                self.msleep(50)  # Sleep to simulate a periodic task (adjust as needed)
        except Exception as e:
            self.error_signal.emit(str(e))  # Emit error if something goes wrong
        finally:
            self.end_signal.emit()  # Signal that the thread has finished

    def stop(self):
        """Stop the worker thread."""
        self.running = False
        self.wait()  # Wait for the thread to exit cleanly