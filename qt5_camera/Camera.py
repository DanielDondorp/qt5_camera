import cv2
import numpy as np
from PyQt5 import QtCore
import threading

class Signals(QtCore.QObject):
    signal_frame_changed = QtCore.pyqtSignal(np.ndarray)
    signal_framerate_changed = QtCore.pyqtSignal(float)

class Camera(threading.Thread):
    def __init__(self, camera_index, framerate, gamma):
        threading.Thread.__init__(self)
        self.signals = Signals()
        self.running = False
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)
        self.gamma = gamma
        self.framerate = framerate
        self.actual_framerate = self.cap.get(cv2.CAP_PROP_FPS)

    def run(self):
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.signals.signal_frame_changed.emit(frame)
        self.cap.release()

    @property
    def gamma(self):
        return self._gamma
    @gamma.setter
    def gamma(self, gamma):
        self._gamma = gamma
        self.cap.set(cv2.CAP_PROP_GAMMA, gamma)
    @property
    def framerate(self):
        return self._framerate
    @framerate.setter
    def framerate(self, framerate):
        self._framerate = framerate
        self.cap.set(cv2.CAP_PROP_FPS, framerate)
        self.actual_framerate = self.cap.get(cv2.CAP_PROP_FPS)