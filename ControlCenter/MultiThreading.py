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


from PyQt5.QtCore import QThread, pyqtSignal, QRunnable, QThreadPool, QMutex, QWaitCondition


class WorkerThread(QThread):
    update_signal = pyqtSignal(object) # signal to send updates to the main thread
    begin_signal = pyqtSignal()     # signal to send begin work to the main thread
    end_signal = pyqtSignal()    # signal to send end work to the main thread
    error_signal = pyqtSignal(str) # in case there some mishap

    def __init__(self, task, sleep_time = 51,  *args, **kwargs):
        """
        Initialize the worker thread
        the sleep_time parameter is set to 51 as the TIME required for returning an answer through SSH
        is about 51 ms.
        :param task: the callable (function or method) to run in the task
        :param args: positional arguments for the task
        :param kwargs: keyword arguments for the task
        """
        super().__init__()
        self.task = task
        self.sleep_time = sleep_time # in microseconds
        self.args = args
        self.kwargs = kwargs
        self.running = True
        self.paused = False
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()


    def run(self):
        self.begin_signal.emit()
        try:
            while self.running:
                self.mutex.lock()
                if self.paused:
                    self.pause_condition.wait(self.mutex)
                self.mutex.unlock()
                result = self.task(*self.args, **self.kwargs)  # Call the task
                self.update_signal.emit(result)
                self.msleep(self.sleep_time)  # Sleep to simulate a periodic task (adjust as needed)
        except Exception as e:
            self.error_signal.emit(str(e))  # Emit error if something goes wrong
        finally:
            self.end_signal.emit()  # Signal that the thread has finished

    def stop(self):
        """Stop the worker thread."""
        self.running = False
        self.wait()  # Wait for the thread to exit cleanly

    def pause(self):
        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()

    def resume(self):
        self.mutex.lock()
        self.paused = False
        self.pause_condition.wakeAll()
        self.mutex.unlock()

class MoveWorker(QThread):
    update_signal = pyqtSignal(object)
    begin_signal = pyqtSignal()
    end_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, move_obj, sleep_time = 75, parent = None):
        super().__init__(parent)
        self.move_obj = move_obj # Instance of Move class must be passed @ worker creation
        self.running = True
        self.sleep_time = sleep_time

    def run(self):
        #print("[MoveWorker] started...")
        self.begin_signal.emit() # THis has to be connected to something that moves the motor.
        while self.running:
            self.msleep(self.sleep_time)
            in_pos = self.move_obj.check_in_pos()
            try:
                in_pos = int(self.move_obj.check_in_pos())
            except ValueError:
                in_pos = 0
           # print(f"[MoveWorker] check_in_pos: {in_pos}")
            self.update_signal.emit(in_pos)
            if in_pos == 1:
                self.running = False
                #print("[MoveWorker] Move completed, emitting end_signal")
                self.end_signal.emit()
                break
        #print("[MoveWorker] Thread ending")


class SpeedWorker(QRunnable):
    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        self.task()