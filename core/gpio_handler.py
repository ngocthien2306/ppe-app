import Jetson.GPIO as GPIO
from utils.project_config import project_config as cf
import time
from datetime import datetime
import threading

class GPIOHandler:
    def __init__(self):
        self.enzim_yn = False
        self.update_button_style_yn = False
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup([cf.GPIO_RESULT, cf.GPIO_SOUND], GPIO.OUT)
        GPIO.setup([cf.GPIO_ENZIM], GPIO.IN)
        
        # GPIO.add_event_detect(cf.GPIO_ENZIM, GPIO.RISING, callback=self.enzim_event_listener_on, bouncetime=20)
        
        print(GPIO.input(cf.GPIO_ENZIM))
        # lock filter when initialize
        GPIO.output(cf.GPIO_RESULT, GPIO.HIGH)
        GPIO.output(cf.GPIO_SOUND, GPIO.HIGH)
    
    def enzim_event_listener_on(self, channel):
        print('Start enzim')
        value = GPIO.input(cf.GPIO_ENZIM)
        print(value)
        if value == GPIO.HIGH:
            self.enzim_yn = True

        elif value == GPIO.LOW:
            self.enzim_yn = False
            
        self.update_button_style_yn = True
    
        
    def output_sound(self, pass_yn=False):
        # Create a separate thread for the sound output
        sound_thread = threading.Thread(target=self._output_sound_in_thread, args={pass_yn})
        sound_thread.start()

    def _output_sound_in_thread(self, pass_yn):
        if pass_yn:
            for i in range(cf.TIMES_OUTPUT):
                time_now = datetime.now()
                print(f'{time_now}: output {i}')
                GPIO.output(cf.GPIO_SOUND, GPIO.LOW)
                time.sleep(0.2)
                GPIO.output(cf.GPIO_SOUND, GPIO.HIGH)
                time.sleep(0.1)
        else:
            GPIO.output(cf.GPIO_SOUND, GPIO.LOW)
            time.sleep(1)
            GPIO.output(cf.GPIO_SOUND, GPIO.HIGH)
            
    # mode 'ON' =  GPIO.LOW
    
    def output_pass(self, mode="ON"):
            # Create a separate thread for the sound output
        sound_thread = threading.Thread(target=self._output_pass_in_thread, args={mode})
        sound_thread.start()
        
    def _output_pass_in_thread(self, mode='ON'):
        print(mode)
        if mode == 'ON':
            print("PASS")
            GPIO.output(cf.GPIO_RESULT, GPIO.LOW)
            
        else:
            print("FAIL")
            GPIO.output(cf.GPIO_RESULT, GPIO.HIGH)
            
    def cleanup(self):
        GPIO.cleanup()
        
