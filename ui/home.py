import sys
import cv2
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore
from utils.constant import constant as c
from utils.project_config import project_config as cf
from core.gpio_handler import GPIOHandler
import time
import datetime
from utils.image_utils import draw_area_done
from utils.utils import save_image
from utils.logging import CustomLoggerConfig
import threading
from ui.info import InfoWindow
from ui.flash import FlashWindow
import Jetson.GPIO as GPIO

class HomeWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        if cf.CLASSIFY_ENGINE == 'YOLO':
            from core.model_handler import InferenceYOLO as ModelEngine
        elif cf.CLASSIFY_ENGINE == "ANSWOME_BACKBONE":
            from core.model_handler import InferenceSwim as ModelEngine

        self._logic = ModelEngine()
        self.gpio_handler = GPIOHandler()
        self.logger = CustomLoggerConfig.configure_logger()
        self.detect_yn = False
        self.simulate_yn = False
        self.inference_yn = False
        self.curr_value_enzim = 0
        self.curr_value_open = None
        self.is_done_detect = False
        self.curr_status_machine = None
        self.curr_is_wrong_open_door = None
        self.frame_detect_done = None
        
        self.flash_window = FlashWindow()
        self.flash_window.show()
        self.flash_window.raise_()
        self.info_window = InfoWindow()
        self.info_window.close()

        self.init_main_window()
        
        # Create a container widget to hold camera and button
        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(12, 12, 12, 20)
        # Create a QLabel to display the camera feed
        self.camera_label = QLabel(self)

        button_layout = QHBoxLayout()

        self.enzin_label = QPushButton("", self)
        self.enzin_label.setFixedHeight(132)
        self.enzin_label.setFixedWidth(165)
        self.enzin_label.setEnabled(False)
        button_layout.addWidget(self.enzin_label)
        
        button_layout.addSpacing(735)
        button_layout.setContentsMargins(10, 14, 10, 20)

        # Create the second additional button and set its properties
        self.simulate_btn = QPushButton("", self)
        self.simulate_btn.setFixedHeight(132)
        self.simulate_btn.setFixedWidth(156)
        self.simulate_btn.setFocusPolicy(Qt.NoFocus)
        
        self.simulate_btn.clicked.connect(self.on_simulate_btn_click)
        
        # Create a new button and set its properties
        self.info_btn = QPushButton("", self)
        self.info_btn.setFixedHeight(70)
        self.info_btn.setFixedWidth(70)
        self.info_btn.setFocusPolicy(Qt.NoFocus)
        self.info_btn.clicked.connect(self.show_info_screen)
        
        # Add the second button to the layout
        button_layout.addWidget(self.simulate_btn)
        
        center_left_layout = QVBoxLayout()
        center_left_layout.addWidget(self.info_btn, alignment=Qt.AlignRight | Qt.AlignVCenter)
        center_left_layout.setContentsMargins(10, 30, 10, 20)
        
        # Set up the camera_label layout
        camera_layout = QVBoxLayout(self.camera_label)
        # camera_layout.addLayout(button_layout)
        camera_layout.addLayout(center_left_layout) 
        camera_layout.addStretch(1)  # Add stretch to push buttons to the top

        container_layout.addWidget(self.camera_label, 5)
        spacer_item = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        container_layout.addItem(spacer_item)
        
        
        # Create a QLabel to serve as a container for the buttons
        self.button_b_container = QLabel(self)
        self.button_b_container.setFixedHeight(200)  # Set an appropriate height
        self.button_b_container.setStyleSheet(c.BUTTON_BG_PATH)  # Set the path to your image

        # Create QPushButton
        self.button = QPushButton("", self)
        self.button.setEnabled(True)
        self.start_detect_timer = QTimer(self)
        self.start_detect_timer.timeout.connect(self.enable_start_detect_button)
        self.button.clicked.connect(self.start_detect)
        self.button.setFixedHeight(166)
        
        button_b_layout = QHBoxLayout(self.button_b_container)
        self.button_machine = QPushButton("", self)
        self.button_machine.setFixedHeight(132)
        self.button_machine.setFixedWidth(176)
        self.button_machine.setEnabled(False)
        
        self.button_door = QPushButton("", self)
        self.button_door.setFixedHeight(130)
        self.button_door.setFixedWidth(132)
        self.button_door.setEnabled(False)
        
        button_b_layout.setContentsMargins(0, 14, 0, 14)
        button_b_layout.addSpacing(10)
        button_b_layout.addWidget(self.enzin_label)
        button_b_layout.addSpacing(25)
        button_b_layout.addWidget(self.button_machine)
        button_b_layout.addSpacing(38)
        button_b_layout.addWidget(self.button_door)
        button_b_layout.addSpacing(350)
        button_b_layout.addWidget(self.simulate_btn)
        button_b_layout.addSpacing(10)
        
        # container_layout.addSpacing(100)  # Adjust as needed
        container_layout.addWidget(self.button_b_container, 1)
        
        # container_layout.addLayout(button_b_layout, 1)  # 1/5 of the space for the button
        # Set the container widget as the central widget
        self.setCentralWidget(container_widget)

        self.update_button_styles()
        
        # Set up the camera
        self.init_camera()

        # Start the camera when the program starts
        self.start_timer()
        
        self.inference_timer = QTimer(self)

        # set update event gpio
        GPIO.add_event_detect(cf.GPIO_OPEN_DOOR, GPIO.RISING, callback=self.reset, bouncetime=None)

    def init_camera(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
    
    def enable_start_detect_button(self):
        self.button.setEnabled(True)
        self.start_detect_timer.stop()
        self.update_button_styles()
       
    def show_info_screen(self):
        self.info_window.close()
        self.info_window.show()
        self.info_window.raise_()
        self.info_window.showFullScreen()
        
    def init_main_window(self):
        width = 1080
        aspect_ratio = 9 / 16  # 9:16
        height = int(width / aspect_ratio)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet(c.BACKGROUND_PATH)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
    
    def update_button_styles(self):
        machine_status = c.MACHINE_ON_PATH if self.curr_status_machine else c.MACHINE_OFF_PATH
        door_status = c.DOOR_CLOSE_PATH if self.curr_is_wrong_open_door else c.DOOR_OPEN_PATH
        
        self.button_door.setStyleSheet(door_status)
        self.button_machine.setStyleSheet(machine_status)
        self.info_btn.setStyleSheet(c.INFO_PATH)
        enzim_style = c.ENZIN_LABEL_ENZIM_PATH if self.gpio_handler.enzim_yn else c.ENZIN_LABEL_NO_ENZIM_PATH
        self.enzin_label.setStyleSheet(enzim_style)

        if self.simulate_yn or self.gpio_handler.enzim_yn:
            self.simulate_btn.setStyleSheet(c.SIMULATE_PATH)
            self.button.setStyleSheet(c.BUTTON_DONE_PATH if self.detect_yn else c.BUTTON_PATH)
        else:
            self.simulate_btn.setStyleSheet(c.DISABLE_SIMULATE_PATH)
            self.button.setStyleSheet(c.BUTTON_DONE_PATH if self.detect_yn else c.DISABLE_BUTTON_PATH)

    def on_simulate_btn_click(self):
        if not self.detect_yn and not self.gpio_handler.enzim_yn:
            self.simulate_yn = not self.simulate_yn
        self.update_button_styles()
    
    def start_timer(self):
        time.sleep(3)
        self.timer.start(16)  # Update every 33 milliseconds (approximately 30 fps)

    def update_button_by_enzim(self):
        
        value = GPIO.input(cf.GPIO_ENZIM)
        if value != self.curr_value_enzim:
            print(f"curr_value_enzim: {value}")
            
            self.curr_value_enzim = value
            if value == GPIO.LOW:
                
                self.gpio_handler.enzim_yn = True
                self.simulate_yn = True
            elif value == GPIO.HIGH:
                self.gpio_handler.enzim_yn = False
                self.simulate_yn = False
                self.gpio_handler.output_pass("OFF")
                
            self.update_button_styles()
            
    def update_open_door(self):
        if self.curr_value_open != self.simulate_yn:
            self.curr_value_open = self.simulate_yn
            if not self.gpio_handler.enzim_yn and not self.curr_value_open:
                self.gpio_handler.output_pass('OFF')
            # else:
            #     self.gpio_handler.output_pass('ON')
                
    def update_status_machine(self):
        value = GPIO.input(cf.GPIO_MACHINE_RUN)
        if self.curr_status_machine != value:
            print(f"curr_status_machine: {value}")
            self.curr_status_machine = value
            if value == GPIO.LOW:
                if self.gpio_handler.enzim_yn or self.simulate_yn:
                    self.inference_yn = True
                    self.button.setEnabled(False)
                    self.inference_timer.start(800)
                    self.start_detect_timer.start(800)
                else:
                    self.inference_yn = False
                    self.inference_timer.stop()
            else:
                self.frame_detect_done = None
                self.inference_yn = False
                self.inference_timer.stop()
                
            self.update_button_styles()
            
    def update_status_error_door(self):
        value = GPIO.input(cf.GPIO_OPEN_DOOR)
        if self.curr_is_wrong_open_door != value:
            print(f"curr_is_wrong_open_door: {value}")
            self.curr_is_wrong_open_door = value
            # if value == GPIO.LOW:
            #     self.frame_detect_done = None
            # else:
            #     self.inference_yn = False
            #     self.inference_timer.stop()
            self.update_button_styles()
            
    def reset(self, channel):
        print(channel)
        self.frame_detect_done = None
        if self.curr_status_machine == GPIO.LOW:
            if self.gpio_handler.enzim_yn or self.simulate_yn:
                self.inference_yn = True
                self.button.setEnabled(False)
                self.inference_timer.start(800)
                self.start_detect_timer.start(800)
            else:
                self.inference_yn = False
        else:
            self.inference_yn = False
            
        self.gpio_handler.output_pass("OFF")
        
            
    def start_detect(self):
        time_now = str(datetime.datetime.now())
        
        if self.simulate_yn or self.gpio_handler.enzim_yn or (not self.simulate_yn and not self.gpio_handler.enzim_yn and self.detect_yn):
            self.detect_yn = not self.detect_yn
            if not self.inference_yn:
                self.gpio_handler.output_pass("OFF")
        
        if self.detect_yn:
            self.inference_yn = True
            self.button.setEnabled(False)
            self.inference_timer.start(800)
            self.start_detect_timer.start(800)
        else: 
            self.update_button_styles()    
            self.frame_detect_done = None   
            self.is_done_detect = False  
    
    def update(self):
        try: 
            self.update_button_by_enzim()
            self.update_open_door()
            self.update_status_machine()
            self.update_status_error_door()
            
            size = self.camera_label.size()
            size_list = [size.width(), size.height()]

            ret, frame = self.camera.read()
            if ret:
                
                if self.is_done_detect:
                    output_frame, _, is_wrong = self._logic.update(frame, size_list, False, False, False)
                else:
                    output_frame, _, is_wrong = self._logic.update(
                        frame, 
                        size_list, 
                        self.detect_yn, 
                        self.simulate_yn, 
                        self.curr_status_machine
                    )
                    
                if self.inference_yn and is_wrong: # and self.inference_timer.remainingTime() > 0:
                    output_frame = draw_area_done(output_frame, is_wrong)
                    self.handle_output(output_frame, is_wrong, mode="ON")
                    self.frame_detect_done = output_frame
                    
                # elif self.inference_yn and not is_wrong: # and self.inference_timer.remainingTime() == 0:
                #     self.handle_output(output_frame, is_wrong, mode='OFF')
                    
                if self.frame_detect_done is not None:
                    self.show_image(self.frame_detect_done)
                else:
                    self.show_image(output_frame)
                    
                self.flash_window.close()
                
                self.gpio_handler.initialize_ready_output()
                
            else:
                self._reconnect_camera()
                
        except Exception as e:
            self.logger.error(f"Exception durring update frame: {e}", exc_info=True)
    
    def _reconnect_camera(self):
        self.logger.warning("Failed to read from the camera. Trying to reconnect...")
        self.camera.release()
        time.sleep(5)
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    def show_image(self, output_frame):
        # self.flash_window.hide()
        height, width, _ = output_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(output_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        self.camera_label.setPixmap(QPixmap.fromImage(q_image))
    
    def handle_output(self, output_frame, is_wrong, mode=None):
        
        time_now = str(datetime.datetime.now())
        time_remaining = self.inference_timer.remainingTime()
        print(f"{time_now}: {time_remaining}")
        
        if mode == 'ON':
            self.gpio_handler.output_sound(pass_yn=(True if mode == 'ON' else False))
        # self.is_done_detect = True

        if is_wrong:
            self.inference_yn = False
            self.inference_timer.stop()
        
        self.update_button_styles()
        self.gpio_handler.output_pass(mode)
        img_path = save_image(image=output_frame, result=is_wrong, img_size=cf.IMAGE_SIZE)
        self.logger.info(f"Handle classify successful! result: {is_wrong} path: {img_path}")

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
            else:
                self.simulate_yn = True
                
            self.update_button_styles()