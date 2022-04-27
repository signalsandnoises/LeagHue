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

# League constants
patch = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
data_dragon_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/"
# Hue constants
config = ConfigParser()
config.read('config.ini')
address = config["Philips Hue"]['bridge_address']
user = config["Philips Hue"]['user']
key = config["Philips Hue"]['key']
groupID = config["Philips Hue"]['group_id']
groupType = config["Philips Hue"]['group_type']

base_request_url = f"https://{address}/clip/v2/resource"

champion = "Seraphine"
skinID = 3

# From a championID and skinID, get the url to query its splash art.
# If none is given, generate the url for a random skin's splash.
def splash_url(championID=None, skinID=None) -> str:
    if championID is None or skinID is None:
        allChampionData = requests.get(data_dragon_url+"champion.json").json()["data"]
        randomChampionID = random.choice(list(allChampionData.keys()))
        randomChampionData = requests.get(f"{data_dragon_url}champion/{randomChampionID}.json").json()
        numberOfSkins = len(randomChampionData["data"][randomChampionID]["skins"])
        randomSkinID = random.randint(0, numberOfSkins)
        championID = randomChampionID
        skinID = randomSkinID
    return f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{championID}_{skinID}.jpg"


# Fetch from url and return image as np array.
# Returns None if no image is found.
def load_image(url) -> np.ndarray:
    res = requests.get(url)
    if res.status_code != 200:
        return None
    img = np.array(Image.open(BytesIO(res.content)))
    return img

url = splash_url(champion, skinID)
print(url)
img = load_image(url)
if img is None:
    raise ImportError("Unable to fetch splash art for this skin!")

queryman = QueryManager(config)


scene_name = f"{champion}_{skinID}"
scene_id = model.img_to_scene(img, scene_name, queryman=queryman, debugging=True)

queryman.recall_dynamic_scene(scene_id)
plt.show()
queryman.delete_scene(scene_id)
