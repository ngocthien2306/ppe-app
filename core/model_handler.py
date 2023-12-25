from utils.project_config import project_config as cf
from ultralytics import YOLO
from utils.image_utils import box_label
from utils.image_utils import center_crop, resize_image, add_margin_to_polygon, draw_area
from utils.inference import inference_model, init_model, show_result_pyplot
from utils.train_utils import get_info, file2dict
from models.build import BuildNet
import torch
import cv2
import os

class InferenceBase:
    def __init__(self, model_path: str = "", conf=None):
        self._model = None  # Initialize this in the derived classes
        self.x1, self.y1, self.x2, self.y2 = cf.RECTANGLES[0]
        self._first_time = True
    def _preprocess(self, frame, size_list):
        frame_copy = frame.copy()
        frame_copy = cv2.rotate(frame_copy, cv2.ROTATE_90_CLOCKWISE)
        frame_copy = resize_image(frame_copy, size_list[0])
        frame_crop = center_crop(frame_copy, size_list)
        frame_resize = cv2.resize(frame_crop, tuple(size_list))
        frame_resize = cv2.flip(frame_resize, 1)
        frame_crop = frame_resize[self.y1:self.y2, self.x1:self.x2]
        return frame_crop.copy(), frame_resize

    def _predict(self, frame):
        raise NotImplementedError("Subclasses must implement this method")

    def _output(self, frame, prob, cls_id, detect_yn):

        frame = box_label(
            frame,
            cf.RECTANGLES[0],
            prob,
            'OK' if cls_id == 1 else 'NG',
            cf.COLORS_MAPPING[cls_id]
        )
        ms = 20  # margin size
        area_config = [[ms, ms],
                    [frame.shape[1] - ms, ms],
                    [frame.shape[1] - ms, frame.shape[0] - ms],
                    [ms, frame.shape[0] - ms]]
        if detect_yn:
            if cls_id == 0:
                frame = draw_area(area_config, frame)
            else:
                frame = draw_area(area_config, frame, (64, 174, 110))

        return frame

    def update(self, frame, img_size, detect_yn, start_yn):
        frame_crop, frame_resize = self._preprocess(frame, img_size)
        if start_yn or self._first_time:
            self._first_time = False
            prob, cls_id = self._predict(frame_crop)
            frame_plot = self._output(frame_resize, prob, cls_id, detect_yn)
            return frame_plot, frame_crop, cls_id
        else:
            return frame_resize, frame_crop, False

class InferenceYOLO(InferenceBase):
    def __init__(self, model_path: str = "", conf=None):
        super().__init__(model_path, conf)
        self._model = YOLO(cf.MODEL_PATH)

    def _predict(self, frame):
        results = self._model.predict(frame, verbose=False)
        cls_id = results[0].probs.top1
        probs = results[0].probs.top1conf.cpu().numpy()
        return probs, cls_id == 1

class InferenceSwim(InferenceBase):
    def __init__(self, model_path: str = "", conf=None):
        super().__init__(model_path, conf)
        self._classes_names, self._label_names = get_info(cf.ANOTATION_PATH)
        model_cfg, train_pipeline, self._val_pipeline, data_cfg, lr_config, optimizer_cfg = file2dict(
            cf.CLASSIFY_ENGINE_PATH)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model_base = BuildNet(model_cfg)
        self._model = init_model(model_base, data_cfg, device=device, mode='eval')

    def _predict(self, frame):
        result = inference_model(self._model, frame, self._val_pipeline, self._classes_names, self._label_names)
        return result['pred_score'], result['pred_label'] == 1

