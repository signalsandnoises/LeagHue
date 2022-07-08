# A development script to experiment on pulling Hue colors from splash art.
# This file uses the deprecated phue library, which uses the deprecated PHue art.


from matplotlib import pyplot as plt
from configparser import ConfigParser
from QueryManager import QueryManager
import model
from time import time
from GameState import GameManager

# EDIT THESE
championName = "Morgana"
skinID = 47

supertick = time()

tick = time()
(championRawID, skinRawID) = GameManager.get_community_dragon_info(championName, skinID)
img = GameManager.get_champion_img(championRawID, skinRawID)
tock = time()
print(f"1. Fetch an image: {tock - tick:.2f}s")

config = ConfigParser()
config.read('../config.ini')
tick = time()
queryman = QueryManager(config)
tock = time()
print(f"2. Construct QueryManager: {tock - tick:.2f}s")


scene_name = f"{championName}_{skinID}"
tick = time()
# TODO look at expensive image processing here
scene_id = model.img_to_scene(img, scene_name, queryman=queryman, debugging=True)
tock = time()
print(f"3. model.img_to_scene: {tock - tick:.2f}s")

supertock = time()
print(f"Total duration: {supertock-supertick:.2f} s")

queryman.recall_dynamic_scene(scene_id)
queryman.delete_scene(scene_id)
plt.show()
queryman.set_color()

