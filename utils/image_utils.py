import cv2
import numpy as np
from utils.project_config import project_config

def center_crop(img, dim):
	"""Returns center cropped image
	Args:
	img: image to be center cropped
	dim: dimensions (height, width) to be cropped
	"""
	width, height = img.shape[1], img.shape[0]

	# process crop width and height for max available dimension
	crop_width = dim[0] if dim[0]<img.shape[1] else img.shape[1]
	crop_height = dim[1] if dim[1]<img.shape[0] else img.shape[0] 
	mid_x, mid_y = int(width/2), int(height/2)
	cw2, ch2 = int(crop_width/2), int(crop_height/2) 
	crop_img = img[mid_y-ch2:mid_y+ch2, mid_x-cw2:mid_x+cw2]
    
	return crop_img

def resize_image(image, target_width):
    original_height, original_width = image.shape[:2]
    scale_factor = target_width / original_width
    new_height = int(original_height * scale_factor)
    resized_image = cv2.resize(image, (target_width, new_height))

    return resized_image


def center_crop_width(img, crop_width):
    """
    Returns center cropped image by keeping the height constant.

    Args:
    img: image to be center cropped
    crop_width: width to be cropped
    """
    width, height = img.shape[1], img.shape[0]

    # Process crop height for the current height
    crop_height = height if crop_width > width else int(crop_width * (height / width))
    
    mid_x, mid_y = int(width / 2), int(height / 2)
    cw2, ch2 = int(crop_width / 2), int(crop_height / 2)
    
    crop_img = img[mid_y - ch2:mid_y + ch2, mid_x - cw2:mid_x + cw2]

    return crop_img

def scale_image(img, factor=1):
	"""Returns resize image by scale factor.
	This helps to retain resolution ratio while resizing.
	Args:
	img: image to be scaled
	factor: scale factor to resize
	"""
	return cv2.resize(img,(int(img.shape[1]*factor), int(img.shape[0]*factor)))

def box_label(frame, box, conf= 0.0, label='', color=(128, 128, 128), text_color=(255, 255, 255)):
    lw = max(round(sum(frame.shape) / 2 * 0.0001), 5)  # line width
    p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
    cv2.rectangle(frame, p1, p2, color, thickness=lw, lineType=cv2.LINE_AA)

    tf = max(lw - 1, 1)  # font thickness
    w, h = cv2.getTextSize(label + ' - ' + str(round(100 * conf, 1)), 0, fontScale=lw / 3, thickness=tf)[0]  # text width, height
    outside = p1[1] - h >= 3
    p2 = p1[0] + w + 130, p1[1] - h - 3 if outside else p1[1] + h + 30
    cv2.rectangle(frame, p1, p2, color, -1, cv2.LINE_AA)  # filled
    cv2.putText(frame,
                label + ' - ' + str(round(100 * conf, 2)) + '%', (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                0,
                lw / 2.5,
                text_color,
                thickness=tf,
                lineType=cv2.LINE_AA)
    
    return frame
    
def draw_area(area_config, image, color=(60, 76, 231)):
    overlay = image.copy()
    area_config_numpy = np.array(area_config)
    cv2.fillPoly(overlay, pts=[area_config_numpy], color=color)
    overlay = cv2.polylines(overlay, [area_config_numpy.reshape((-1, 1, 2))], True, project_config.LINE_AREA_COLOR, 2)
    image = cv2.addWeighted(overlay, project_config.TRANSPARENT_SCORE, image, 1 - project_config.TRANSPARENT_SCORE, 0)
    return image


def draw_area_done(frame, cls_id):
    ms = 20  # margin size
    area_config = [[ms, ms],
                [frame.shape[1] - ms, ms],
                [frame.shape[1] - ms, frame.shape[0] - ms],
                [ms, frame.shape[0] - ms]]
    

    if cls_id == 0:
        frame = draw_area(area_config, frame)
    else:
        frame = draw_area(area_config, frame, (64, 174, 110))

    return frame


def add_margin_to_polygon(original_points, margin):
    # Extract coordinates of the original points
    x_coords, y_coords = zip(*original_points)

    # Calculate the margins
    x_margin = margin
    y_margin = margin

    # Calculate the new coordinates with margin
    new_points = [
        (min(x_coords) - x_margin, min(y_coords) - y_margin),
        (max(x_coords) + x_margin, min(y_coords) - y_margin),
        (min(x_coords) - x_margin, max(y_coords) + y_margin),
        (max(x_coords) + x_margin, max(y_coords) + y_margin),
    ]

    return new_points