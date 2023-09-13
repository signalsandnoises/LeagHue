# LeagHue is developed by Rishabh Verma (https://github.com/vermarish)
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
import sys

logging.basicConfig(
	filename="debug.log",
	level=logging.DEBUG,
	format='%(asctime)s %(levelname)-8s %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S'
)

def exceptionHandler(type, value, traceback):
	logging.exception(f"Uncaught exception", exc_info=(type, value, traceback))
sys.excepthook = exceptionHandler


# disable warnings of "insecure" requests to the local game API
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Hue constants
config = ConfigParser()
config.read('config.ini')
gamedata_url = "https://127.0.0.1:2999/liveclientdata/allgamedata/"

logging.info("Waiting for game..")


## Main loop
while True:
	initialized = False

	# We'll detect for gamestart by determining whether the gamedata_url 404s
	try:
		response = requests.get(gamedata_url, verify=False, timeout=3)
	except:
		# Game's not running yet.
		response = None
		sleep(10)

	if response is not None:
		# ensure the QueryManager is initialized ASAP
		if not initialized:
			logging.info("Game client is running, game has not yet started.")
			queryman = QueryManager(config)
			initialized = True
		json = response.json()
		if 'events' in json:  # wait for the game to officially start
			logging.debug("Game is providing events")
			if len(json['events']['Events']) > 0:
				logging.debug("Game has provided first event")
				intergame_state = queryman.get_light_states()

				# The GameManager object takes care of the entire League game upon instantiation
				# It "finishes construction" only once the game is no longer running.
				# This design avoids asynchronous design and permits encapsulation of all activities during
				# game phase within the GameManager object.
				game_manager = GameManager(queryman, json)

				queryman.apply_light_states(intergame_state)

		sleep(0.05) # We poll at 20 Hz if the HTTP connection works but the game hasn't started.