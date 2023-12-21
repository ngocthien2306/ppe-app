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

if cf.CLASSIFY_ENGINE == 'YOLO':
    from core.model_handler import InferenceYOLO as ModelEngine
elif cf.CLASSIFY_ENGINE == "ANSWOME_BACKBONE":
    from core.model_handler import InferenceSwim as ModelEngine
    
class CollectWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self._logic = ModelEngine()
        self.logger = CustomLoggerConfig.configure_logger()
        self.detect_yn = False
        self.simulate_yn = False
        self.inference_yn = False
        self.sound_yn = False
        self.frame_crop = None
        
        self.init_main_window()

        # Create a container widget to hold camera and button
        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(12, 12, 12, 40)
        # Create a QLabel to display the camera feed
        self.camera_label = QLabel(self)

        button_layout = QHBoxLayout()

        self.enzin_label = QPushButton("", self)
        self.enzin_label.setFixedHeight(132)
        self.enzin_label.setFixedWidth(160)
        self.enzin_label.setEnabled(False)
        button_layout.addWidget(self.enzin_label)
        button_layout.addSpacing(735)
        button_layout.setContentsMargins(10, 14, 10, 20)

        # Create the second additional button and set its properties
        self.simulate_btn = QPushButton(self.count_sample_text(), self)
        font = QFont()
        font.setPointSize(20)
        self.simulate_btn.setFont(font)
        self.simulate_btn.setFixedHeight(132)
        self.simulate_btn.setFixedWidth(300)
        

        # Add the second button to the layout
        button_layout.addWidget(self.simulate_btn)

        # Set up the camera_label layout
        camera_layout = QVBoxLayout(self.camera_label)
        camera_layout.addLayout(button_layout)
        camera_layout.addStretch(1)  # Add stretch to push buttons to the top

        container_layout.addWidget(self.camera_label, 4)
        spacer_item = QSpacerItem(0, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        container_layout.addItem(spacer_item)
        
        # Create buttons
        self.pass_button = QPushButton("", self)
        self.fail_button = QPushButton("", self)

        # Set attributes for Pass button
        self.pass_button.setEnabled(True)
        self.pass_button.setFixedHeight(166)
        self.pass_button.setFixedWidth(510)
        self.pass_button.clicked.connect(self.pass_action)

        # Set attributes for Fail button
        self.fail_button.setEnabled(True)
        self.fail_button.setFixedWidth(510)
        self.fail_button.setFixedHeight(166)
        self.fail_button.clicked.connect(self.fail_action)

        # Create horizontal layout and add buttons to it
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.pass_button)
        self.button_layout.addWidget(self.fail_button)
        
        container_layout.addLayout(self.button_layout, 1)  # 1/5 of the space for the button

        # Set the container widget as the central widget
        self.setCentralWidget(container_widget)

        self.update_button_styles()
        
        # Set up the camera
        self.init_camera()

        # Start the camera when the program starts
        self.start_timer()
        
    def pass_action(self):
        img_path = os.path.join(cf.COLLECT_PATH, 'ok', f"{time.time()}_pass.png")
        cv2.imwrite(img_path, self.frame_crop)
        self.update_simulate_button_text()

    def fail_action(self):
        img_path = os.path.join(cf.COLLECT_PATH, 'ng', f"{time.time()}_fail.png")
        cv2.imwrite(img_path, self.frame_crop)
        self.update_simulate_button_text()

    def update_simulate_button_text(self):
        self.simulate_btn.setText(self.count_sample_text())

    def count_sample_text(self):
        import glob
        fail_list_paths = glob.glob(os.path.join(cf.COLLECT_PATH, 'ng', '*.png'))
        pass_list_paths = glob.glob(os.path.join(cf.COLLECT_PATH, 'ok', '*.png'))
        return "Pass: {0} \n Fail: {1}".format(str(len(pass_list_paths)), str(len(fail_list_paths)))

    def init_camera(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        
    def init_main_window(self):
        width = 1080
        aspect_ratio = 9 / 16  # 9:16
        height = int(width / aspect_ratio)
        self.setGeometry(100, 100, width, height)
        self.setStyleSheet(c.BACKGROUND_PATH)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
    
    def update_button_styles(self):
        # self.enzin_label.setStyleSheet(c.ENZIN_LABEL_NO_ENZIM_PATH)
        self.pass_button.setStyleSheet(c.PASS_PATH)
        self.fail_button.setStyleSheet(c.FAIL_PATH)
    
    def start_timer(self):
        time.sleep(3)
        self.timer.start(16)  # Update every 33 milliseconds (approximately 30 fps)

          
    def update(self):
        try: 
            size = self.camera_label.size()
            size_list = [size.width(), size.height()]
            ret, frame = self.camera.read()
            if ret:
                output_frame, frame_crop, is_wrong = self._logic.update(frame, size_list, self.detect_yn, True)
                self.frame_crop = frame_crop.copy()
                self.show_image(output_frame)
                    
            else:
                print('Failed to read from the camera. Trying to reconnect...')
                # Release the previous camera instance
                self.camera.release()
                # Introduce a short delay before retrying
                time.sleep(5)
                # Try to connect to the camera again
                self.camera = cv2.VideoCapture(0)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                
        except Exception as e:
            self.logger.error(f"Exception durring update frame: {e}", exc_info=True)
    
    def show_image(self, output_frame):
        height, width, _ = output_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(output_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        self.camera_label.setPixmap(QPixmap.fromImage(q_image))
    
    def closeEvent(self, event):
        # Stop the camera when the application is closed
        self.camera.release()
        self.timer.stop()
        self.gpio_handler.cleanup()
        super().closeEvent(event)
        
    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key_Q:
            sys.exit()
            
        elif event.key() == Qt.Key_S:
            self.gpio_handler.enzim_yn = not self.gpio_handler.enzim_yn
            if not self.gpio_handler.enzim_yn:
                self.simulate_yn = False
                self.start_detect = False
            self.update_button_styles()
            
        