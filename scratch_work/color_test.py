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

tick = time()

# League constants
patch = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
data_dragon_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/"
# Hue constants
config = ConfigParser()
config.read('../config.ini')
address = config["Philips Hue"]['bridge_address']
user = config["Philips Hue"]['user']
key = config["Philips Hue"]['key']
groupID = config["Philips Hue"]['group_id']
groupType = config["Philips Hue"]['group_type']

base_request_url = f"https://{address}/clip/v2/resource"

championName = "Ashe"
skinID = 0

championRosterURL = "http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
championRoster = requests.get(championRosterURL).json()  # TODO might fail
championRosterEntryGet = [entry for entry in championRoster if entry['name'] == championName]
championRosterEntry = championRosterEntryGet[0]
championRawID: int = championRosterEntry["id"]
skinRawID: int = 1000*championRawID + skinID

splashURL = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/{championRawID}/{skinRawID}.jpg"
res = requests.get(splashURL)
if res.status_code == 404:
	chromaURL = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-chroma-images/{championRawID}/{skinRawID}.png"
	res = requests.get(chromaURL)
if res.status_code != 200:
	raise ConnectionError(f"Error code {res.status_code} when getting art for {skinRawID}.")
img = np.array(Image.open(BytesIO(res.content)))

n_pixels = np.shape(img)[0]*np.shape(img)[1]
while n_pixels > 500000:
    img = img[::2,::2]
    n_pixels = np.shape(img)[0]*np.shape(img)[1]

if np.shape(img)[2] == 4:  # then it's RGBA. convert to RGB.
    # strategy: all pixels with alpha < 255 are sent to blank white
    transparent_mask = img[:,:,3] < 255
    img[transparent_mask] = [255,255,255,255]
    img = img[:,:,0:3]


tock = time()
print(f"Startup (image fetching): {tock - tick}")

tick = time()
queryman = QueryManager(config)
tock = time()
print(f"QueryManager constructor: {tock - tick}")


scene_name = f"{championName}_{skinID}"
tick = time()
scene_id = model.img_to_scene(img, scene_name, queryman=queryman, debugging=True)
tock = time()
print(f"Model: {tock - tick}")
queryman.recall_dynamic_scene(scene_id)
queryman.delete_scene(scene_id)
plt.show()
queryman.set_color()
