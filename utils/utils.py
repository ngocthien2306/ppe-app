import time
import os
import cv2

def get_path_log(log_path='tracks', sub_path='fail'):
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

def box_label(frame, box, conf= 0.0, label='', color=(128, 128, 128), text_color=(255, 255, 255)):
    lw = max(round(sum(frame.shape) / 2 * 0.0005), 2)  # line width
    p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
    cv2.rectangle(frame, p1, p2, color, thickness=lw, lineType=cv2.LINE_AA)

    tf = max(lw - 1, 1)  # font thickness
    w, h = cv2.getTextSize(label, 0, fontScale=lw / 3, thickness=tf)[0]  # text width, height
    outside = p1[1] - h >= 3
    p2 = p1[0] + w + 130, p1[1] - h - 3 if outside else p1[1] + h + 30
    cv2.rectangle(frame, p1, p2, color, -1, cv2.LINE_AA)  # filled
    cv2.putText(frame,
                label + ' - ' + str(round(100 * conf, 1)), (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                0,
                lw / 2.5,
                text_color,
                thickness=tf,
                lineType=cv2.LINE_AA)

