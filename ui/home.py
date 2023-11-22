import sys
import cv2
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore
from utils.image_utils import center_crop

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up the main window with a 9:16 aspect ratio
        width = 600
        aspect_ratio = 9 / 16  # 9:16
        height = int(width / aspect_ratio)
        self.detect_yn = False
        self.setGeometry(100, 100, width, height)
        self.setStyleSheet("background-image: url('ui/assets/images/background.png'); background-position: center;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        # Create a container widget to hold camera and button
        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)

        # Create a QLabel to display the camera feed
        self.camera_label = QLabel(self)
        container_layout.addWidget(self.camera_label, 4)  # 4/5 of the space for camera

        # Create QPushButton
        self.button = QPushButton("KIỂM TRA PPE", self)
        self.button.clicked.connect(self.start_detect)
        self.button.setFont(QFont("Roboto", 64, weight=400))  # Set font size and make it bold
        self.button.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #147EC4, stop:1 #5CA1CF); color: white; border: none")

        icon = QIcon("ui/assets/icon/icons8-circled-play-100.png")  # Replace with the actual path to your icon file
        self.button.setIcon(icon)
        self.button.setIconSize(QtCore.QSize(100, 100))  # Set the icon size
        self.button.setFixedHeight(100)
        
        self.button_original_stylesheet = self.button.styleSheet()
        
        container_layout.addWidget(self.button, 1)  # 1/5 of the space for the button

        # Set the container widget as the central widget
        self.setCentralWidget(container_widget)

        # OpenCV variables
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)

        # Start the camera when the program starts
        self.start_camera()

    
    def start_camera(self):
        # Start the camera
        self.timer.start(33)  # Update every 33 milliseconds (approximately 30 fps)

    def revert_button_appearance(self):
        self.button.setStyleSheet(self.button_original_stylesheet)
    
    def start_detect(self):
        self.detect_yn = not self.detect_yn
        if self.detect_yn:
            self.button.setText('REFRESH DETECT')
            self.button.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2E86C1, stop:1 #3498DB); color: white; border: none")
            QTimer.singleShot(500, self.revert_button_appearance)
            
            icon = QIcon("ui/assets/icon/icons8-refresh-100.png")  # Replace with the actual path to your icon file
            self.button.setIcon(icon)
            self.button.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E67E22, stop:1 #F5B041); color: white; border: none")
            self.button_original_stylesheet = self.button.styleSheet()
        
        else:
            self.button.setText("KIỂM TRA PPE")
            self.button.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EB984E, stop:1 #F8C471); color: white; border: none")
            QTimer.singleShot(500, self.revert_button_appearance)
            
            icon = QIcon("ui/assets/icon/icons8-circled-play-100.png")  # Replace with the actual path to your icon file
            self.button.setIcon(icon)
            self.button.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #147EC4, stop:1 #5CA1CF); color: white; border: none")
            self.button_original_stylesheet = self.button.styleSheet()
            
    def update_camera(self):
        size = self.camera_label.size()
        size_list = [size.width(), size.height()]

        ret, frame = self.camera.read()
        if ret:
            frame_copy = frame.copy()
            frame_crop = center_crop(frame_copy, size_list)  # Crop width, keeping height constant
            resized_image = cv2.resize(frame_crop, tuple(size_list))

            height, width, _ = resized_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(resized_image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

            # Set the QImage as the pixmap for the QLabel
            self.camera_label.setPixmap(QPixmap.fromImage(q_image))
        
    def closeEvent(self, event):
        # Stop the camera when the application is closed
        self.camera.release()
        self.timer.stop()
        super().closeEvent(event)
        
    def keyPressEvent(self, event):
        # Exit the program if 'q' is pressed
        if event.key() == Qt.Key_Q:
            sys.exit()
            
            