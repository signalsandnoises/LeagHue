# On first run, you will have to press your Philips Bridge
# button and start the script within 30 seconds (unless
# you've used phue.Bridge before).

from time import sleep
import requests
import urllib3
import LightManager
import GameState
from json import loads

## parameters go here
#  TODO store these and load from a config.txt file
ip = "10.0.0.50"
active_IDs = [4,5]
username = "t9EuSmHFC2o7bTtt5Lyq5eUMKNU0otLLN4nHE9wO"

# TODO awful python naming schemes why
light_manager = LightManager.LightManager(active_IDs, ip, username)

## The League client is https only with an insecure cert. 
#  We'll just.. suppress it for now. It's all on localhost 
#  anyway, who's going to invade us?  TODO
urllib3.disable_warnings()

league_address = "https://127.0.0.1:2999/liveclientdata/allgamedata/"

i = 1
## Main loop
while True:
	try:
		response = requests.get(league_address, verify=False, timeout=3)
	except:
		# Game's not running yet.
		print(str(i) + ": not running")
		response = None
		initialized = False
		next_event_id = 0
		i += 1

	if response is not None:  # Client's running.
		json = response.json()
		if 'events' in json:  # wait for the game to officially start
			if len(json['events']['Events']) > 0:
				print("Game started.")

				intergame_state = light_manager.get_state()

				# TODO I hate this file/class naming
				game_manager = GameState.GameManager(light_manager, json)

				# Once the GameManager exits, we go back to the usual state and poll at 0.5 Hz through the try/except clause
				light_manager.apply_state(loads(intergame_state))
		sleep(0.05) # We poll at 20 Hz if the HTTP connection works but the game hasn't started.

			



	
''' This app will be structured so that it queries the League API every second when inactive.
When it gets a successful query, we start querying every 0.1 seconds.

Events:
	death: (de-saturate, then reset upon respawn)
	ace: (rainbow)
	victory: turn blue, then reset after 10s
	defeat: turn red, then reset after 10s


On initialization, we create a LightManager which manages the lighting environment.

In the main-loop, we query to detect whether the game has started, once per second. Once it has,
we construct GameState.

The GameState is initialized with a champion and their skin. It tracks all in-game events.


Create a 

'''




## League API address
#response = requests.get("​https://127.0.0.1:2999/liveclientdata/allgamedata/")
#print(response.json())