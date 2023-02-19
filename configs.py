import yaml
from enum import Enum


DEFAULT_CONFIG_FILE = 'default.yaml'

def load_config(file):
    with open(file, 'rb')as f:
        cfg = yaml.load(f.read(), Loader=yaml.FullLoader)
    return cfg

def save_config(cfg, file):
    s = yaml.dump(cfg)
    with open(file, 'w') as f:
        f.write(s)
    return True

class MODE(Enum):
    DRAW_MODE = 0
    VIEW_MODE = 1

class DISPLAY(Enum):
    ELEVATION = 0
    RGB = 1
    CATEGORY = 2
    INSTANCE = 3
