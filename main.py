# On first run, you will have to press your Philips Bridge
# button and start the script within 30 seconds (unless
# you've used phue.Bridge before).

from phue import Bridge
from time import sleep
import requests
import urllib3

## parameters
#  TODO store these and load from config.txt
ip = "10.0.0.52"
active_IDs = [3,4,5]
username = "t9EuSmHFC2o7bTtt5Lyq5eUMKNU0otLLN4nHE9wO"

## The League client is https only with an insecure cert. 
#  We'll just.. suppress it for now. It's all on localhost 
#  anyway, who's going to invade?
urllib3.disable_warnings()

## To interface with lights through phue.py
b = Bridge(ip)
lights = b.get_light_objects('id')

## To interface with lights through http
base_address = '/'.join(['http:/',
	ip,
	"api",
	username,
	"lights"])
# a dictionary containing each light's address from which to query
address = {ID: '/'.join([base_address, str(ID)]) for ID in active_IDs}


## Store the vertices of each light's color gamut
gamut_vertices = {}
for ID in active_IDs:
	gamut_vertices[ID] = requests.get(address[ID]).json()['capabilities']['control']['colorgamut']


def rainbow(IDs, time_per_cycle=2, cycles=1):
	init_vals = {ID: requests.get(address[ID]).json()['state']['xy'] for ID in IDs}
	#init_vals = {ID: requests.get('/'.join([address, str(ID)])).json()['state']['xy'] for ID in IDs}

	for cycle in range(cycles):
		for i in range(3):
			for ID in IDs:
				lights[ID].transitiontime = time_per_cycle*10/3
				lights[ID].xy=gamut_vertices[ID][i]
			sleep(time_per_cycle/3)

	for ID in IDs:
		lights[ID].transitiontime=40
		lights[ID].xy = init_vals[ID]



league_address = "​https://127.0.0.1:2999/liveclientdata/allgamedata/"
while True:
	try:
		response = requests.get(league_address, verify=False)
	except:
		response = None
		initialized = False
		next_event_id = 0
		sleep(1)

	if response is not None:  # then we're live!
		json = response.json()
		if not initialized:  # let's store the summoner's info and their skin
			summonerName = json["activePlayer"]["summonerName"]
			playerIndex = 0
			while json["allPlayers"][playerIndex]["summonerName"] != summonerName:
				playerIndex += 1
			if playerIndex >= 10:
				print("Somehow, this game has eleven players..")
				print("or none of the players match the current user.")
				break

			# Now we have their playerIndex, and can get their playerInfo!
			playerInfo = json["allPlayers"][playerIndex]
			championName = playerInfo[championName]
			formattedName = "".join(championName.split())  # Master Yi's URL is .../MasterYi.json
			skinID = playerInfo["skinID"]
			team = playerInfo["team"]

			# TODO this needs to be auto-loaded somehow according to the latest patch
			data_dragon_url = "https://ddragon.leagueoflegends.com/cdn/11.6.1/data/en_US/champion/" + formattedName
			skinName = requests.get(data_dragon_url)["data"][formattedName]["skins"][skinID]["name"]



	
''' This app will be structured so that it queries the League API every second when inactive.
When it gets a successful query, we start querying every 0.1 seconds.

Events:
	death: (de-saturate, then reset upon respawn)
	ace: (rainbow)
	victory: turn blue, then reset after 10s
	defeat: turn red, then reset after 10s

On
'''




## League API address
#response = requests.get("​https://127.0.0.1:2999/liveclientdata/allgamedata/")
#print(response.json())