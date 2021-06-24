from PyQt5 import QtCore
import cv2
import time
import threading

class Writer(QtCore.QThread):
    signal_writing_started = QtCore.pyqtSignal()
    signal_writing_stopped = QtCore.pyqtSignal()

    def __init__(self, q, n_frames, savepath, framerate, shape):
        QtCore.QThread.__init__(self)
        self.q = q
        self.n_frames = n_frames
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
        frames_written = 0
        self.running = True
        self.signal_writing_started.emit()
        while self.running:
            frame = self.q.get()
            self.out.write(frame)
            self.q.task_done()
            frames_written += 1
            if frames_written >= self.n_frames:
                self.running = False
        self.signal_writing_stopped.emit()