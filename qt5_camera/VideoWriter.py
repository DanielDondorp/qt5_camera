from PyQt5 import QtCore
import cv2
import time
import threading

class Timer(QtCore.QThread):
    signal_timer_started = QtCore.pyqtSignal()
    signal_timer_stopped = QtCore.pyqtSignal()
    signal_time_progressed = QtCore.pyqtSignal(float)
    def __init__(self, duration):
        QtCore.QThread.__init__(self)
        self.duration = duration
        self.running = True

    def run(self):
        start_time = time.time()
        i = 0
        while self.running:
            time_elapsed = time.time() - start_time
            if time_elapsed >= self.duration:
                self.running = False
            else:
                if i % 10 == 0:
                    self.signal_time_progressed.emit(time_elapsed)
                time.sleep(0.01)
                i+=1
        self.signal_timer_stopped.emit()


class Writer(QtCore.QThread):
    signal_writing_started = QtCore.pyqtSignal()
    signal_writing_stopped = QtCore.pyqtSignal()

    def __init__(self, q, savepath, framerate, shape):
        QtCore.QThread.__init__(self)
        self.q = q
        ext = savepath.split(".")[-1].lower()
        if ext == "mp4":
            fourcc =  cv2.VideoWriter_fourcc(*"mp4v")
        elif ext == "avi":
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
        else:
            print(f"extension {ext} not supported. Writing avi with XVID encoding.")
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.out = cv2.VideoWriter(savepath, fourcc, framerate, shape, isColor = False)
        self.running = False

    def run(self):
        self.running = True
        self.signal_writing_started.emit()
        while self.running:
            frame = self.q.get()
            if type(frame)==(str):
                self.running=False
                print(frame)
            else:
                self.out.write(frame)
                self.q.task_done()
        self.out.release()
        self.signal_writing_stopped.emit()
