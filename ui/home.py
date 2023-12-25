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
import threading

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
        self.simulate_yn = False
        self.curr_value_enzim = 0
        self.is_done_detect = False
        self.curr_status_machine = None
        self.curr_is_wrong_open_door = None
        self.frame_detect_done = None
        self.count_sound = 0
        
        self.flash_window = FlashWindow()
        self.flash_window.show()
        self.flash_window.raise_()
        self.info_window = InfoWindow()
        self.info_window.close()

        self.init_main_window()
        
        # Create a container widget to hold camera and button
        container_widget = QWidget(self)
        container_layout = QHBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        # Create a QLabel to display the camera feed
        self.camera_label = QLabel(self)

        button_layout = QVBoxLayout()

        self.enzin_label = QPushButton("", self)
        self.enzin_label.setFixedHeight(132)
        self.enzin_label.setFixedWidth(165)
        self.enzin_label.setEnabled(False)
        button_layout.addWidget(self.enzin_label)
        
        # button_layout.setContentsMargins(10, 14, 10, 14)

        # Create the second additional button and set its properties
        self.simulate_btn = QPushButton("", self)
        self.simulate_btn.setFixedHeight(132)
        self.simulate_btn.setFixedWidth(155)
        self.simulate_btn.setFocusPolicy(Qt.NoFocus)
        
        self.simulate_btn.clicked.connect(self.on_simulate_btn_click)
        
        # Create a new button and set its properties
        self.info_btn = QPushButton("", self)
        self.info_btn.setFixedHeight(70)
        self.info_btn.setFixedWidth(70)
        self.info_btn.setFocusPolicy(Qt.NoFocus)
        self.info_btn.clicked.connect(self.show_info_screen)
        
        self.collect = QPushButton("", self)
        self.collect.setFixedHeight(100)
        self.collect.setFixedWidth(100)
        self.collect.setFocusPolicy(Qt.NoFocus)
        self.collect.clicked.connect(self.show_collect_screen)
        
        # Add the second button to the layout
        button_layout.addWidget(self.simulate_btn)
        

        # center_right_layout.setContentsMargins(10, 10, 10, 10)
        
        center_left_layout = QVBoxLayout()
        center_left_layout.addWidget(self.info_btn)

        center_right_layout = QVBoxLayout()
        center_right_layout.addWidget(self.collect)
        # center_left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Set up the camera_label layout
        camera_layout = QVBoxLayout(self.camera_label)
        
        camera_layout.addLayout(center_right_layout) 
        camera_layout.addLayout(center_left_layout) 

        camera_layout.addStretch(1)  # Add stretch to push buttons to the top

        container_layout.addWidget(self.camera_label, 4)
        container_layout.addSpacing(0)
        
        # Create a QLabel to serve as a container for the buttons
        self.button_b_container = QLabel(self)
        self.button_b_container.setFixedWidth(250)  # Set an appropriate height
        self.button_b_container.setStyleSheet(c.BUTTON_BG_PATH)  # Set the path to your image
        
        button_b_layout = QVBoxLayout(self.button_b_container)
        self.button_machine = QPushButton("", self)
        self.button_machine.setFixedHeight(132)
        self.button_machine.setFixedWidth(176)
        self.button_machine.setEnabled(False)
        
        self.button_door = QPushButton("", self)
        self.button_door.setFixedHeight(130)
        self.button_door.setFixedWidth(132)
        self.button_door.setEnabled(False)
        
        # button_b_layout.setContentsMargins(14, 14, 14, 14)
        button_b_layout.addSpacing(10)
        button_b_layout.addWidget(self.enzin_label, alignment=QtCore.Qt.AlignCenter)
        button_b_layout.addSpacing(20)
        button_b_layout.addWidget(self.button_machine, alignment=QtCore.Qt.AlignCenter)
        button_b_layout.addSpacing(20)
        button_b_layout.addWidget(self.button_door, alignment=QtCore.Qt.AlignCenter)
        button_b_layout.addSpacing(270)
        button_b_layout.addWidget(self.simulate_btn, alignment=QtCore.Qt.AlignCenter)
        button_b_layout.addSpacing(10)

        container_layout.addWidget(self.button_b_container, 1)
        
        # Set the container widget as the central widget
        self.setCentralWidget(container_widget)

        self.update_button_styles()
        
        # Set up the camera
        self.init_camera()

        # Start the camera when the program starts
        self.start_timer()
        self.inference_timer = QTimer(self)
        
    def init_camera(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

    def show_collect_screen(self):
        print("show_collect_screen")
        self.camera.release()
        self.timer.stop()
        self.close()

        from ui.collect_data import CollectWindow
        collect_window = CollectWindow()
        collect_window.show()
        collect_window.raise_()
        collect_window.showFullScreen()
        
    
    def show_info_screen(self):
        self.info_window.close()
        self.info_window.show()
        self.info_window.raise_()
        self.info_window.showFullScreen()
        
    def init_main_window(self):
        width = 1920
        aspect_ratio = 9 / 16  # 9:16
        height = int(width * aspect_ratio)
        self.setGeometry(0, 0, width, height)
        self.setStyleSheet(c.BACKGROUND_PATH)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
    
    def update_button_styles(self):
        
        machine_status = c.MACHINE_ON_PATH if self.curr_status_machine == cf.STATE_MACHINE else c.MACHINE_OFF_PATH
        door_status = c.DOOR_CLOSE_PATH if self.curr_is_wrong_open_door == cf.STATE_DOOR else c.DOOR_OPEN_PATH
        
        self.button_machine.setStyleSheet(machine_status)
        self.button_door.setStyleSheet(door_status)
        
        self.info_btn.setStyleSheet(c.INFO_PATH)
        
        enzim_style = c.ENZIN_LABEL_ENZIM_PATH if self.gpio_handler.enzim_yn == cf.STATE_ENZYME else c.ENZIN_LABEL_NO_ENZIM_PATH
        self.enzin_label.setStyleSheet(enzim_style)

        if self.simulate_yn or self.gpio_handler.enzim_yn == cf.STATE_ENZYME:
            self.simulate_btn.setStyleSheet(c.SIMULATE_PATH)
        else:
            self.simulate_btn.setStyleSheet(c.DISABLE_SIMULATE_PATH)

    def on_simulate_btn_click(self):
        if self.gpio_handler.enzim_yn != cf.STATE_ENZYME:
            self.simulate_yn = not self.simulate_yn
            
        if self.frame_detect_done is not None: 
            self.simulate_yn = True
            
        self.update_button_styles()
    
    def start_timer(self):
        time.sleep(3)
        self.timer.start(16)  # Update every 33 milliseconds (approximately 30 fps)

    def update_button_by_enzim(self):
        value = GPIO.input(cf.GPIO_ENZIM)
        if value != self.curr_value_enzim:
            print(f"curr_value_enzim: {value}")
            self.curr_value_enzim = value
            self.gpio_handler.enzim_yn = value
            
            if self.curr_value_enzim == cf.STATE_ENZYME:
                self.simulate_yn = True
            else:
                self.simulate_yn = False

    def update_status_machine(self):
        value = GPIO.input(cf.GPIO_MACHINE_RUN)
        if value != self.curr_status_machine:
            print(f"curr_status_machine: {value}")
            self.curr_status_machine = value
            
    def update_status_error_door(self):
        value = GPIO.input(cf.GPIO_OPEN_DOOR)
        if value != self.curr_is_wrong_open_door:
            print(f"curr_is_wrong_open_door: {value}")
            if self.curr_is_wrong_open_door != cf.STATE_DOOR and value == cf.STATE_DOOR:
                self.reset_ui_and_interlock()
            self.curr_is_wrong_open_door = value
         
    def reset_ui_and_interlock(self):
        self.frame_detect_done = None
        self.handle_output(None, None, mode="OFF")
        self.count_sound = 0
            
    def reset_program(self):
        self.update_status_machine()
        # if self.curr_status_machine == cf.STATE_MACHINE:
        self.reset_ui_and_interlock()
            
    def update_logic(self):
        
        # create threading for each function
        thread_button = threading.Thread(target=self.update_button_by_enzim)
        thread_machine = threading.Thread(target=self.update_status_machine)
        thread_error_door = threading.Thread(target=self.update_status_error_door)

        thread_button.start()
        thread_machine.start()
        thread_error_door.start()

        # wait the functions done
        thread_button.join()
        thread_machine.join()
        thread_error_door.join()
        
        self.update_button_styles()
        
        
    def update(self):
        self.update_logic()
        try: 
            size = self.camera_label.size()
            size_list = [size.width(), size.height()]
            ret, frame = self.camera.read()

            # cv2.imwrite('test.png', frame)
            
            if ret:
                output_frame, _, is_wrong = self._logic.update(frame, size_list, False, self.simulate_yn)
                if (self.curr_status_machine != cf.STATE_MACHINE 
                    and (self.curr_value_enzim == cf.STATE_ENZYME or self.simulate_yn)
                    and is_wrong and self.count_sound == 0):
                        
                    self.count_sound += 1
                    output_frame = draw_area_done(output_frame, is_wrong)
                    self.is_done_detect = True
                    self.frame_detect_done = output_frame
                    self.handle_output(output_frame, is_wrong, mode="ON")
                
                if self.frame_detect_done is not None:
                    self.show_image(self.frame_detect_done)
                else:
                    self.show_image(output_frame)
                    
                self.reset_program()
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
        height, width, _ = output_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(output_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        self.camera_label.setPixmap(QPixmap.fromImage(q_image))
    
    def handle_output(self, output_frame=None, is_wrong=None, mode=None):
        self.gpio_handler.output_sound(pass_yn=(True if mode == 'ON' else False))
        self.gpio_handler.output_pass(mode)
        if output_frame is not None:
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