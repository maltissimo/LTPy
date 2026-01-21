import threading

from Graphics.Base_Classes_graphics.BaseClasses import myWarningBox


def synchronized_method(method):
    outer_lock = threading.Lock()
    lock_name = "__" + method.__name__ + "__lock" + "__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name): setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock: return method(self, *args, **kws)

    return sync_method


from PyQt5.QtCore import QThread, pyqtSignal, QRunnable, QThreadPool, QMutex, QWaitCondition, QMutexLocker


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

    def __init__(self, move_obj, sleep_time = 90, parent = None):
        super().__init__(parent)
        self.move_obj = move_obj # Instance of Move class must be passed @ worker creation
        self.running = True
        self.sleep_time = sleep_time

    def run(self):
        #print("[MoveWorker] started...")
        self.begin_signal.emit() # THis has to be connected to something that moves the motor.
        while self.running:
            self.msleep(self.sleep_time)
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


class CoordMessenger():
    """
    This class is intended to act as a multi-threading messenger to and from the Gantry.
    The goal is JUST to receive motor coordinates, and to pass those as a dictionary out.

    """

    def __init__(self, connection, sleep_time=51):
        self.worker = WorkerThread(task=self.get_and_update_coords, sleep_time=sleep_time)
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()
        self.paused = False
        self.connection = connection

        if not self.connection or self.connection.alive == False:
            conn_warning = myWarningBox(title="Warning!",
                                        message="PMAC Connection not active!")
            conn_warning.show_warning()

        self.coordinates = {
            "X": 0.0,
            "Y": 0.0,
            "Z": 0.0,
            "pitch": 0.0,
            "roll": 0.0,
            "yaw": 0.0
        }

        self.worker.update_signal.connect(self.update_coordinates)
        self.worker.end_signal.connect(self.stop)
        self.worker.begin_signal.connect(self.start)
        self.worker.error_signal.connect(self.handleworkererror)

    def get_and_update_coords(self):
        self.mutex.lock()
        while self.paused:
            self.pause_condition.wait(self.mutex)
        self.mutex.unlock()
        self.connection.send_receive("&1,2,3p")
        response = self.connection.textoutput
        #print(response)

        return(response)

    def update_coordinates(self, response):
        flag = 0
        #print("update method called, with result: ", response)
        response = list(response)
        if not response:
            return
        try:
            """if response[0] != '&1,2,3p':
                print("full Response: ", response)
                flag =1"""
            while response and response[0] != '&1,2,3p':
                response.pop(0)
            """ The two lines above clean the PMAC response, so that only coordinates are received. """
            """if flag == 0:
                print("Cleaned response: ", response)
                flag = 0"""
            if len(response) < 4:
                return # this avoids crashes from not-well formed responses. since the update is rapid this should not be an issue
            CS1 = response[1].split()
            CS2 = response[2].split()
            CS3 = response[3].split()
            
            # Check if we have enough data in the split strings to avoid IndexError
            if len(CS1) < 3 or len(CS2) < 1 or len(CS3) < 2:
                # print(f"Malformed coordinate response: {response}")
                return

            #print("CS1: " + str(CS1) + "\nCS2 : " +str(CS2) + "\nCS3: " + str(CS3))
            with QMutexLocker(self.mutex):
                self.coordinates.update({
                    "pitch" : float(CS1[1][1:]),
                    "roll": float(CS1[0][1:]),
                    "Z": float(CS1[2][1:]),
                    "yaw": float(CS2[0][1:]),
                    "X": float(CS3[0][1:]),
                    "Y": float(CS3[1][1:])
                })
                """for key in self.coordinates :
                    print(key, self.coordinates[key])"""

        except ValueError as e:
            get_coord_warning = myWarningBox(title="Error",
                                         message=str(e))
            get_coord_warning.show_warning()
    def pause(self):
        self.worker.pause()
    def resume(self):
        self.worker.resume()

    def start(self):
        if not self.worker.isRunning():
            self.worker.start()

    def stop(self):
        self.worker.stop()

    def handleworkererror(self, message):
        worker_warning = myWarningBox(title="Error",
                                      message=str(message))
        worker_warning.show_warning()
