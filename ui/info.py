import sys
import cv2
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore
from utils.image_utils import center_crop, resize_image
from utils.constant import constant as c
from utils.project_config import project_config as cf
import time
import datetime
import logging
from utils.utils import save_image
from utils.logging import CustomLoggerConfig
import threading
import os

class InfoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.logger = CustomLoggerConfig.configure_logger()
        self.init_main_window()

        # Create a container widget to hold camera and button
        container_widget = QWidget(self)
        container_layout = QHBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        # Create a QLabel to display the camera feed
        self.camera_label = QLabel(self)

        container_layout.addWidget(self.camera_label, 4)
        # spacer_item = QSpacerItem(0, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # container_layout.addItem(spacer_item)
        
        # Create buttons
        self.close_button = QPushButton("", self)

        # Set attributes for Pass button
        self.close_button.setEnabled(True)
        self.close_button.setFixedHeight(166)
        self.close_button.clicked.connect(self.close_window)

        # Create horizontal layout and add buttons to it
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.close_button)
        
        container_layout.addLayout(self.button_layout, 1)  # 1/5 of the space for the button

        # Set the container widget as the central widget
        self.setCentralWidget(container_widget)
        self.show_background()
        self.update_button_styles()
        
    def init_main_window(self):
        width = 1920
        aspect_ratio = 9 / 16  # 9:16

        height = int(width * aspect_ratio)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet(c.BACKGROUND_PATH)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
    
    def update_button_styles(self):
        self.close_button.setStyleSheet(c.CLOSE_PATH)
    
    def start_timer(self):
        time.sleep(3)
        self.timer.start(16)  # Update every 33 milliseconds (approximately 30 fps)

    def show_background(self):
        img = cv2.imread(c.INFO_BACKGROUND_PATH)
        self.show_image(img)
     
    def show_image(self, output_frame):
        height, width, _ = output_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(output_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        self.camera_label.setPixmap(QPixmap.fromImage(q_image))
    
    def close_window(self):
        self.hide()
    
    def closeEvent(self, event):
        super().closeEvent(event)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            sys.exit()