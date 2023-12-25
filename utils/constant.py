from pydantic import BaseSettings
import os
from utils.project_config import project_config as cf

def generate_style(path):
    return f"background-image: url('{path}'); background-position: center; color: white; border: none"

def icon_path(name):
    return os.path.join(cf.ROOT_UI_PATH, name)

class Constant(BaseSettings):
    SIMULATE_PATH: str = generate_style(icon_path("detect-on.png"))
    BUTTON_DONE_PATH: str = generate_style(icon_path("Button highligt done.png"))
    BUTTON_PATH: str = generate_style(icon_path("Button highligt detect.png"))
    ENZIN_LABEL_ENZIM_PATH: str = generate_style(icon_path("enzim-on.png"))
    ENZIN_LABEL_NO_ENZIM_PATH: str = generate_style(icon_path("enzim-off.png"))
    DISABLE_SIMULATE_PATH: str = generate_style(icon_path("detect-off.png"))
    DISABLE_BUTTON_PATH: str = generate_style(icon_path("Disable Detect Button highligt.png"))
    BACKGROUND_PATH: str = generate_style(icon_path("Mask group landscape.png"))
    PASS_PATH: str = generate_style(icon_path("button pass.png"))
    FAIL_PATH: str = generate_style(icon_path("button fail.png"))
    INFO_PATH: str = generate_style(icon_path("About.png"))
    CLOSE_PATH: str = generate_style(icon_path("Button Close.png"))
    INFO_BACKGROUND_PATH: str = icon_path("Info.png")
    LOADING_BACKGROUND_PATH: str = generate_style(icon_path("ai_background_1920.png"))
    DOOR_CLOSE_PATH: str = generate_style(icon_path("door-close.png"))
    DOOR_OPEN_PATH: str = generate_style(icon_path("door-open.png"))
    MACHINE_ON_PATH: str = generate_style(icon_path("machine-on.png"))
    MACHINE_OFF_PATH: str = generate_style(icon_path("machine-off.png"))
    BUTTON_BG_PATH: str = generate_style(icon_path("Rectangle 208.png"))
    

constant = Constant()
    