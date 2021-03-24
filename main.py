# On first run, you will have to press your Philips Bridge
# button and start the script within 30 seconds (unless
# you've used phue.Bridge before).

from time import sleep
import requests
import urllib3

## parameters
#  TODO store these and load from config.txt
ip = "10.0.0.52"
active_IDs = [3,4,5]
username = "t9EuSmHFC2o7bTtt5Lyq5eUMKNU0otLLN4nHE9wO"

light_manager = LightManager(active_IDs, ip, username)

## The League client is https only with an insecure cert. 
#  We'll just.. suppress it for now. It's all on localhost 
#  anyway, who's going to invade us?  TODO
urllib3.disable_warnings()

league_address = "​https://127.0.0.1:2999/liveclientdata/allgamedata/"

## Main loop
while True:
	try:
		response = requests.get(league_address, verify=False)
	except:
		# Game's not running yet.
		response = None
		initialized = False
		next_event_id = 0
		sleep(1)

	if response is not None:  # Game's running.
		json = response.json()

		# If we've just started,
		if not initialized:
			# Let's get the playerIndex.
			summonerName = json["activePlayer"]["summonerName"]
			playerIndex = 0
			while json["allPlayers"][playerIndex]["summonerName"] != summonerName:
				playerIndex += 1
			if playerIndex >= 10:
				# TODO can i just delete this if-block?
				print("Somehow, this game has eleven players..")
				print("or none of the players match the current user.")
				break

			# Now that we have playerIndex, let's get playerInfo
			playerInfo = json["allPlayers"][playerIndex]
			championName = playerInfo[championName]
			skinID = playerInfo["skinID"]
			team = playerInfo["team"]

			# To obtain skinName:
			# championName -> championID 
			# championID + skinID -> skinName

			# TODO there exists no consistent function to get a champions "[id].json". 
			#      See Kog'Maw -> KogMaw.json, Cho'Gath -> Chogath.json.
			#      Gonna have to find a mapping somewhere

			# TODO this needs to be auto-loaded somehow according to the latest patch
			# TODO can region be configured?	
			data_dragon_url = "https://ddragon.leagueoflegends.com/cdn/11.6.1/data/en_US/"

			allChampionData = requests.get(data_dragon_url+"champion.json").json()["data"]
			# keys are championIDs
			# vals are attributes including championName
			championID = None
			for key in allChampionData:
				val = allChampionData[key]["name"]
				if championName == val:
					championID = key
			if championID == None:
				# TODO does this happen?
				print("Oh no we brokes it. Can't get a champion's internal ID. How will we ever get skinName?")

			skinName = requests.get(data_dragon_url+"champion/"+championID+".json")["data"][championID]["skins"][skinID]["name"]
			state = db_manager.get_state(skinName)
			



	
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