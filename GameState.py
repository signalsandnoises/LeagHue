# TODO refactor all other mentions of state to "environment"
# when referencing Hue colors.

from json import loads as str2json
import requests
import db_manager
from time import sleep
from QueryManager import QueryManager
import numpy as np
from PIL import Image
from io import BytesIO
import model

class GameManager:

	league_address = "https://127.0.0.1:2999/liveclientdata/allgamedata/"

	# TODO change params
	def __init__(self, queryman: QueryManager, json):
		'''
		Game has begun, first event has occurred.
		Goal: get the skin info and change the color
		Process:
			activePlayer[summonerName] -> allPlayers[playerindex]
			playerIndex -> playerInfo -> championName, skinID
			championName -> championID 
			championID+skinID -> skinName
		Then we can set the color.
		'''
		self.lastEventID = 0
		self.queryman = queryman

		states = queryman.get_light_states()

		queryman.set_color()  # white

		# summonerName -> playerIndex
		self.summonerName = json["activePlayer"]["summonerName"]
		playerIndex = 0
		while json["allPlayers"][playerIndex]["summonerName"] != self.summonerName:
			playerIndex += 1
			if playerIndex >= 10:
				raise AttributeError("Player not found in API")

		# playerIndex -> playerInfo
		playerInfo = json["allPlayers"][playerIndex]

		# playerInfo -> various stuff
		championName = playerInfo["championName"]
		skinID = int(playerInfo["skinID"])
		self.team = playerInfo["team"]

		championRosterURL = "http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
		championRoster = requests.get(championRosterURL).json()  # TODO might fail
		championRosterEntryGet = [entry for entry in championRoster if entry['name'] == championName]
		championRosterEntry = championRosterEntryGet[0]
		championRawID = championRosterEntry["id"]
		# championAlias = championRosterEntry["alias"]  # TODO don't need this
		skinRawID = str(1000*championRawID + skinID)

		# Find skinName by checking skinRawID against every skin and every chroma for that champion
		championInfoURL = f"http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/{championRawID}.json"
		championInfo = requests.get(championInfoURL).json()
		championSkins = championInfo["skins"]
		i = 0
		foundSkin = False
		skinName = championName
		while i < len(championSkins) and not foundSkin:
			if championSkins[i]["id"] == skinRawID:
				foundSkin = True
				skinName = championSkins[i]["name"]
			if "chromas" in championSkins[i].keys():
				chromas = championSkins[i]["chromas"]
				j = 0
				while j < len(chromas) and not foundSkin:
					if chromas[j]["id"] == skinRawID:
						foundSkin = True
						skinName = chromas[j]["name"]
					j += 1
			i += 1

		# Get a good image, whether it's a base character, skin, or chroma
		splashURL = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/{championRawID}/{skinRawID}.jpg"
		res = requests.get(splashURL)
		if res.status_code == 404:
			chromaURL = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-chroma-images/{championRawID}/{skinRawID}.jpg"
			res = requests.get(chromaURL)
		if res.status_code != 200:
			raise ConnectionError(f"Error code {res.status_code} when getting art for {skinRawID}.")
		img = np.array(Image.open(BytesIO(res.content)))

		# big model
		self.scene_id = model.img_to_scene(img, skinName, queryman)

		# apply model result and go into main loop
		queryman.recall_dynamic_scene(self.scene_id)
		self.main_loop()
		queryman.delete_scene(self.scene_id)
		queryman.apply_light_states(states)

	def main_loop(self):
		while True:
			sleep(0.05)
			try:
				response = requests.get(self.league_address, verify=False).json()
			except:
				# Game is no longer running.
				break

			# Let's find out what's happened. Multiple events may occur.
			events = response["events"]["Events"]
			freshEvents = events[self.lastEventID + 1:]

			# Possible events to handle are: GameEnd, Ace.
			for freshEvent in freshEvents:
				eventName = freshEvent["EventName"]

				# If the game ends
				if eventName == "Ace":
					acingTeam = [event["AcingTeam"] for event in freshEvents if event["EventName"] == "Ace"][0]
					if acingTeam == self.team:
						self.queryman.rainbow(self.scene_id)
				elif eventName == "GameEnd":
					result = [event["Result"] for event in freshEvents if event["EventName"] == "GameEnd"][0]
					if result == "Win":
						self.queryman.set_color(x=0.156,y=0.145)  # blue
					else:
						self.queryman.set_color(x=0.678, y=0.3018)  # red
					sleep(4)
					break

				self.lastEventID = freshEvents[-1]["EventID"]