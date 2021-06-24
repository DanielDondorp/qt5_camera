from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtMultimedia import QCameraInfo
from ui.camera_controls_ui import Ui_TileMapWidget as camera_control_ui
import sys
from Camera import Camera
import numpy as np
import cv2
import time


class CameraWidget(QtWidgets.QDockWidget,camera_control_ui):
    def __init__(self):
        QtWidgets.QDockWidget.__init__(self)
        camera_control_ui.__init__(self)
        self.setWindowTitle("Camera Controls")
        self.ui = camera_control_ui()
        self.ui.setupUi(self)
        self.connect_ui()

        self.get_available_cameras()
        self.connect_camera()

    def connect_ui(self):
        self.ui.buttonScanCameras.clicked.connect(self.get_available_cameras)
        self.ui.buttonConnectCamera.clicked.connect(self.connect_camera)
        self.ui.checkBoxViewCamera.toggled.connect(self.toggle_view_camera)

        for framerate in [10,30,60,120,240]:
            self.ui.comboBoxFramerate.addItem(str(framerate))
            self.ui.comboBoxFramerate.setCurrentText("30")

        self.ui.sliderCameraGamma.valueChanged.connect(self.update_camera_gamma)
        self.ui.sliderCameraBrightness.valueChanged.connect(self.update_camera_brightness)
        self.ui.buttonSetFramerate.clicked.connect(self.update_camera_framerate)


    def get_available_cameras(self):
        self.available_cameras = {c.deviceName() : c.description() for c in QCameraInfo.availableCameras()}
        self.ui.comboBoxCameras.clear()
        for cam in self.available_cameras:
            self.ui.comboBoxCameras.addItem(f"{cam} - {self.available_cameras[cam]}")
        print(self.available_cameras)

    def connect_camera(self):
        if hasattr(self, "cam"):
            self.cam.running = False
            time.sleep(0.1)
        device_name = self.ui.comboBoxCameras.currentText().split(" ")[0]

        gamma = self.ui.sliderCameraGamma.value()
        framerate = int(self.ui.comboBoxFramerate.currentText())
        brightness = self.ui.sliderCameraBrightness.value()
        self.cam = Camera(device_name, framerate, gamma, brightness)

        if self.ui.checkBoxViewCamera.isChecked():
            self.cam.signals.signal_frame_changed.connect(self.update_image)

        self.cam.start()

    def toggle_view_camera(self, view_camera):
        if view_camera:
            self.cam.signals.signal_frame_changed.connect(self.update_image)
            self.ui.labelVideoDisplay.setVisible(True)
        else:
            self.cam.signals.signal_frame_changed.disconnect()
            self.ui.labelVideoDisplay.setVisible(False)

    def update_camera_gamma(self, value):
        self.ui.labelCameraGammaValue.setText(str(value/100.0))
        self.cam.gamma = value

    def update_camera_brightness(self, value):
        self.ui.labelCameraBrightnessValue.setText(str(value))
        self.cam.brightness = value
    def update_camera_framerate(self):
        self.connect_camera()
        self.ui.labelFramerate.setText(f"Framerate (currently {self.cam.actual_framerate})")

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, frame):
        qt_img = self.convert_cv_qt(frame)
        self.ui.labelVideoDisplay.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        h, w = cv_img.shape
        ch = 1
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(cv_img.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
        p = convert_to_Qt_format.scaled(1200, 1080, QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)

    def closeEvent(self, event):
        try:
            self.cam.running = False
        except:
            pass
        print("goodbye")
        event.accept()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CameraWidget()
    window.show()
    sys.exit(app.exec_())

