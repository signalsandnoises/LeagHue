# TODO refactor all other mentions of state to "environment"
# when referencing Hue colors.

from json import loads as str2json
import requests
import db_manager
import tkinter as tk
from time import sleep


class GameManager:

	patch = "11.6.1"
	league_address = "https://127.0.0.1:2999/liveclientdata/allgamedata/"


	def __init__(self, light_manager, json):
		'''
		Game has begun, first event has occurred.
		Goal: get the skin info and change the color
		Process:
			activePlayer summonerName -> allPlayers playerindex
			playerIndex -> playerInfo -> championName+skinID
			championName -> championID 
			championID+skinID -> skinName
		Then we can set the color.
		'''
		self.latestEventID = 0;

		self.light_manager = light_manager
		self.light_manager.apply_color(xy=light_manager.WHITE, transitiontime=1, brightness_coeff=0.3)

		# summonerName -> playerIndex
		self.summonerName = json["activePlayer"]["summonerName"]
		playerIndex = 0
		while json["allPlayers"][playerIndex]["summonerName"] != self.summonerName:
			playerIndex += 1
			if playerIndex >= 10:
				# TODO can i just delete this if-block?
				print("Somehow, this game has eleven players..")
				print("or none of the players match the current user.")
				break

		# playerIndex -> playerInfo
		playerInfo = json["allPlayers"][playerIndex]

		# playerInfo -> stuff
		championName = playerInfo["championName"]
		skinID = playerInfo["skinID"]
		self.team = playerInfo["team"]

		# championName -> championID
		
		# TODO this needs to be auto-loaded somehow according to the latest patch
		# TODO can region be configured?	
		data_dragon_url = "https://ddragon.leagueoflegends.com/cdn/{}/data/en_US/".format(self.patch)
		allChampionData = requests.get(data_dragon_url+"champion.json").json()["data"]
		
		championID = None
		for key in allChampionData:
			# keys are championIDs
			# vals are attributes including championName
			val = allChampionData[key]["name"]
			if championName == val:
				championID = key
				break
		if championID == None:
			# TODO does this happen? We might fail to get a champion's ID
			# if we don't have the latest data dragon.
			print("Oh no we brokes it. Can't get a champion's internal ID. How will we ever get skinName?")

		# championID+skinID -> skinName
		championData = requests.get(data_dragon_url+"champion/"+championID+".json").json()
		skins = championData["data"][championID]["skins"]
		skin = [skin for skin in skins if skin['num'] == skinID]
		skin = skin[0]
		self.skinName = skin["name"]
		if self.skinName == 'default':
			self.skinName = championName
		
		state = db_manager.get_state(self.skinName)
		if state is None:
			self.light_manager.apply_color(transitiontime=20)
		else:
			state = ''.join(state.split('\''))  # strip all single quotes.
			state = str2json(state)
			state = {str(key): state[key] for key in state}
			self.light_manager.apply_state(state, transitiontime=20)

		self.main_loop()

	def main_loop(self):
		while True:
			sleep(0.05)
			try:
				response = requests.get(self.league_address, verify=False).json()
			except:
				# Game is no longer running.
				break



	"""
	def main_loop(self):
		command = None
		while command not in ["store", "save", "help"]:
			command = input(">>>")
			command = command.lower()
			if command == "help":
				print("You are using lights " + str(self.light_manager.active_IDs) + ".")
				print("You are currently playing " + self.skinName + ".")
				print("You can adjust these Hue lights and save the configuration for " + self.skinName +
					  " with 'store'")
			if command == "store" or command == "save":
				try:
					state = self.light_manager.get_state()
					db_manager.set_state(self.skinName, str(state))
					print("Stored for " +self.skinName + "!")
				except:
					print("Oh no, something went wrong!")
			else:
				print("Invalid input. See 'help'.")
			command = None
	"""