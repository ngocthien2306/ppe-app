from pydantic import BaseSettings
import os
from utils.project_config import project_config as cf

def generate_style(path):
    return f"background-image: url('{path}'); background-position: center; color: white; border: none"

def icon_path(name):
    return os.path.join(cf.ROOT_UI_PATH, name)

class Constant(BaseSettings):

    SIMULATE_PATH: str = generate_style(icon_path("Simulate.png"))
    BUTTON_DONE_PATH: str = generate_style(icon_path("Button highligt done.png"))
    BUTTON_PATH: str = generate_style(icon_path("Button highligt detect.png"))
    ENZIN_LABEL_ENZIM_PATH: str = generate_style(icon_path("Button highligt enzim.png"))
    ENZIN_LABEL_NO_ENZIM_PATH: str = generate_style(icon_path("Button highligt no enzim.png"))
    DISABLE_SIMULATE_PATH: str = generate_style(icon_path("Disable Button highligt.png"))
    DISABLE_BUTTON_PATH: str = generate_style(icon_path("Disable Detect Button highligt.png"))
    BACKGROUND_PATH: str = generate_style(icon_path("Mask group.png"))
    PASS_PATH: str = generate_style(icon_path("button pass.png"))
    FAIL_PATH: str = generate_style(icon_path("button fail.png"))
    INFO_PATH: str = generate_style(icon_path("About.png"))
    CLOSE_PATH: str = generate_style(icon_path("Button Close.png"))
    INFO_BACKGROUND_PATH: str = icon_path("Info.png")
    LOADING_BACKGROUND_PATH: str = generate_style(icon_path("background.png"))
    

constant = Constant()
    