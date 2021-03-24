# TODO refactor all other mentions of state to "environment"
# when referencing Hue colors.

class GameManager:

	def __init__(self, light_manager, json):
		'''
		Goal: get the skin info and change the color
		Process:
			activePlayer summonerName -> allPlayers playerindex
			playerIndex -> playerInfo -> championName+skinID
			championName -> championID 
			championID+skinID -> skinName
		'''

		# summonerName -> playerIndex
		self.summonerName = json["activePlayer"]["summonerName"]
			playerIndex = 0
			while json["allPlayers"][playerIndex]["summonerName"] != summonerName:
				playerIndex += 1
			if playerIndex >= 10:
				# TODO can i just delete this if-block?
				print("Somehow, this game has eleven players..")
				print("or none of the players match the current user.")
				break

		# playerIndex -> playerInfo
		playerInfo = json["allPlayers"][playerIndex]

		# playerInfo -> stuff
		championName = playerInfo[championName]
		skinID = playerInfo["skinID"]
		self.team = playerInfo["team"]

		# championName -> championID
		
		# TODO this needs to be auto-loaded somehow according to the latest patch
		# TODO can region be configured?	
		data_dragon_url = "https://ddragon.leagueoflegends.com/cdn/11.6.1/data/en_US/"
		
