import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore


class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window with a 9:16 aspect ratio
        width = 600
        aspect_ratio = 9 / 16  # 9:16
        height = int(width / aspect_ratio)
        self.setGeometry(100, 100, width, height)

        # Create a container widget to hold camera and button
        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)

        # Create a QLabel to display the camera feed
        self.camera_label = QLabel(self)
        container_layout.addWidget(self.camera_label, 4)  # 4/5 of the space for camera

        # Create QPushButton
        button = QPushButton("Start Camera", self)
        button.clicked.connect(self.start_camera)
        button.setFont(QFont("Arial", 32, QFont.Bold))  # Set font size and make it bold
        button.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2E86C1, stop:1 #5DADE2); color: white;")

        icon = QIcon("ui/assets/icon/icons8-checkmark-64.svg")  # Replace with the actual path to your icon file
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(44, 44))  # Set the icon size
        button.setFixedHeight(100)
        container_layout.addWidget(button, 1)  # 1/5 of the space for the button

        # Set the container widget as the central widget
        self.setCentralWidget(container_widget)

        # OpenCV variables
        self.camera = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)

        # Start the camera when the program starts
        self.start_camera()

    def start_camera(self):
        # Start the camera
        self.timer.start(33)  # Update every 33 milliseconds (approximately 30 fps)

    def update_camera(self):
        # Read a frame from the camera
        ret, frame = self.camera.read()

        if ret:
            # Convert the OpenCV frame to QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            frame = cv2.flip(frame, 2)
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

            # Set the QImage as the pixmap for the QLabel
            self.camera_label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        # Stop the camera when the application is closed
        self.camera.release()
        self.timer.stop()
        super().closeEvent(event)