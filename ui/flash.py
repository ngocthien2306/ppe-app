import sys
import cv2
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout, QDialog, QApplication
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


class LoadingScreen(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Loading")
        self.setGeometry(300, 300, 300, 100)

        self.label = QLabel("Loading...", self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

class FlashWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.logger = CustomLoggerConfig.configure_logger()
        self.init_main_window()

        # Create a container widget to hold camera and button
        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(12, 12, 12, 60)
        self.setCentralWidget(container_widget)

        # Create an instance of the LoadingScreen
        self.loading_screen = LoadingScreen()

        # Call start_loading_screen method to show the loading screen
        self.start_loading_screen()

    def init_main_window(self):
        width = 1080
        aspect_ratio = 9 / 16  # 9:16
        height = int(width / aspect_ratio)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet(c.LOADING_BACKGROUND_PATH)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

    def start_timer(self):
        time.sleep(3)
        self.timer.start(16)  # Update every 33 milliseconds (approximately 30 fps)

    def start_loading_screen(self):
        self.simulate_long_running_task()
        
    def simulate_long_running_task(self):
        # Simulate a long-running task (replace this with your actual task)
        for i in range(150):
            QApplication.processEvents()
            # Simulate some work
            import time
            time.sleep(0.05)