# A development script to experiment on pulling Hue colors from splash art.
# This file uses the deprecated phue library, which uses the deprecated PHue art.

import requests
import random
import numpy as np
from PIL import Image
from io import BytesIO
from matplotlib import pyplot as plt
from configparser import ConfigParser
from colorlib import *
from QueryManager import QueryManager
import model
from time import time
from GameState import GameManager


champion = "Morgana"
skinID = 24


img = GameManager.get_champion_img(champion, skinID)


# TODO our RGBA->RGB conversion is flawed. Example:
# plt.imshow(GameManager.get_champion_img("Morgana", 25)

config = ConfigParser()
config.read('../config.ini')
tick = time()
queryman = QueryManager(config)
tock = time()
print(f"QueryManager constructor: {tock - tick}")


scene_name = f"{champion}_{skinID}"
tick = time()
# TODO look at expensive image processing here
scene_id = model.img_to_scene(img, scene_name, queryman=queryman, debugging=True)
tock = time()
print(f"Model: {tock - tick}")
queryman.recall_dynamic_scene(scene_id)
plt.show()
queryman.delete_scene(scene_id)
