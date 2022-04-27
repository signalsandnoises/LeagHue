# A development script to experiment on pulling Hue colors from splash art.
# This file uses the deprecated phue library, which uses the deprecated PHue art.

import requests
import random
import numpy as np
from PIL import Image
from io import BytesIO
import urllib3
from configparser import ConfigParser
from colorlib import *
from QueryManager import QueryManager
from GameState import GameManager
from time import sleep
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

gamedata_url = "https://127.0.0.1:2999/liveclientdata/allgamedata/"
base_request_url = f"https://{address}/clip/v2/resource"

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

queryman = QueryManager(config)

i = 1
## Main loop
while True:
	try:
		response = requests.get(gamedata_url, verify=False, timeout=3)
	except:
		# Game's not running yet.
		print(str(i) + ": not running")
		response = None
		initialized = False
		next_event_id = 0
		i += 1
		sleep(10)

	if response is not None:  # Client's running.
		json = response.json()
		if 'events' in json:  # wait for the game to officially start
			if len(json['events']['Events']) > 0:
				print("Game started.")
				intergame_state = queryman.get_light_states()

				# The GameManager object takes care of the entire League game upon instantiation
				# It "finishes construction" only once the game is no longer running.
				game_manager = GameManager(queryman, json)

				queryman.apply_light_states(intergame_state)

		sleep(0.05) # We poll at 20 Hz if the HTTP connection works but the game hasn't started.



## The League client is https only with an insecure cert.
#  We'll just.. suppress it for now. It's all on localhost
#  anyway, who's going to invade us?  TODO
urllib3.disable_warnings()

league_address = "https://127.0.0.1:2999/liveclientdata/allgamedata/"











scene_name = f"{champion}_{skinID}"
scene_id = model.img_to_scene(img, scene_name, queryman=queryman)
queryman.recall_dynamic_scene(scene_id)

queryman.delete_scene(scene_id)
