import os
from utils.project_config import project_config as cf
import cv2 

def get_path_log(log_path='tracks', sub_path=''):
    from datetime import datetime, time
    shifts = [['06:00:00', '13:59:59', 'shift-1'],
              ['14:00:00', '21:59:59', 'shift-2'],
              ['22:00:00', '06:59:59', 'shift-3']]

    current_time = str(datetime.now().time())
    current_shift = ''

    for shift in shifts:
        if shift[0] <= current_time <= shift[1]:
            current_shift = shift[2]
            break

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    today = str(datetime.now().date())
    day_path = os.path.join(log_path, today)
    if not os.path.exists(day_path):
        os.makedirs(day_path)

    shift_path = os.path.join(day_path, current_shift)
    if not os.path.exists(shift_path):
        os.makedirs(shift_path)

    sub_path_check = os.path.join(shift_path, sub_path)
    if not os.path.exists(sub_path_check):
        os.makedirs(sub_path_check)

    return str(os.path.join(sub_path_check, str(current_time))).replace(':', '_').replace('.', '_')


def save_image(image, result: bool, extension: str = '.png'):
    img_path = get_path_log(os.path.join(cf.LOG_PATH, 'log_pass' if result else 'log_fail')) + extension
    cv2.imwrite(img_path, image)
    return img_path 
    