# LeagHue is developed by Rishabh Verma (https://github.com/vermarish)
# If you're
#
# This file contains the main loop for LeagHue. Its general structure is as follows:
#  * Wait 10 seconds at a time to see if a game has begun loading (idle)
#    * Once a game has begun loading, wait 0.05 seconds at a time to see if the game has started (active)
#    * Once the game has started, get the current light state and pass control to GameManager.
#    * Once the game has ended, apply the saved light state and return to idle.


import requests
from configparser import ConfigParser
from QueryManager import QueryManager
from GameState import GameManager
from time import sleep
import logging

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

# Hue constants
config = ConfigParser()
config.read('config.ini')
gamedata_url = "https://127.0.0.1:2999/liveclientdata/allgamedata/"
queryman = QueryManager(config)

logging.info("Waiting for game..")
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

	if response is not None:
		logging.info("Game client is running")
		json = response.json()
		if 'events' in json:  # wait for the game to officially start
			logging.info("Game is providing events")
			if len(json['events']['Events']) > 0:
				print("GameStart event")
				intergame_state = queryman.get_light_states()

				# The GameManager object takes care of the entire League game upon instantiation
				# It "finishes construction" only once the game is no longer running.
				game_manager = GameManager(queryman, json)

				queryman.apply_light_states(intergame_state)

		logging.debug("Game client has not started.")
		sleep(0.05) # We poll at 20 Hz if the HTTP connection works but the game hasn't started.