# Contains code to monitor the League of Legends game client and retrieve associated game information from
# external websites

import requests
from time import sleep
from QueryManager import QueryManager
import numpy as np
from PIL import Image
from io import BytesIO
import model
import logging

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
        logging.info("Set to white")

        # summonerName -> playerIndex
        self.summonerName = json["activePlayer"]["summonerName"]
        playerIndex = 0
        while json["allPlayers"][playerIndex]["summonerName"] != self.summonerName:
            playerIndex += 1
            if playerIndex >= 10:
                logging.error("Player not found in API")

        # playerIndex -> playerInfo
        playerInfo = json["allPlayers"][playerIndex]

        # playerInfo -> championName and skinID
        championName = playerInfo["championName"]
        skinID: int = playerInfo["skinID"]
        self.team = playerInfo["team"]

        (championRawID, skinRawID) = GameManager.get_community_dragon_info(championName, skinID)
        img = GameManager.get_champion_img(championRawID, skinRawID)

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

        logging.info(f"Summoned {skinName} ({championName}, {skinID})")
        logging.debug(f"Community Dragon details: championRawID {championRawID}, skinRawID {skinRawID}")

        self.scene_id = model.img_to_scene(img, skinName, queryman)

        logging.debug(f"Computed scene {self.scene_id}")

        # apply model result and go into main loop
        queryman.recall_dynamic_scene(self.scene_id)
        self.main_loop()
        logging.info("Game ended")
        queryman.delete_scene(self.scene_id)
        queryman.apply_light_states(states)

    @staticmethod
    def get_community_dragon_info(championName: str, skinID: int) -> (int, int):
        # championName and skinID -> championRawID + skinRawID (for community dragon)
        championRosterURL = "http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
        championRoster = requests.get(championRosterURL).json()  # TODO might fail
        championRosterEntryGet = [entry for entry in championRoster if entry['name'] == championName]
        championRosterEntry = championRosterEntryGet[0]
        championRawID: int = championRosterEntry["id"]
        skinRawID = 1000 * championRawID + skinID
        return championRawID, skinRawID


    @staticmethod
    def get_champion_img(championRawID, skinRawID):
        # Get a good image, whether it's a base character, skin, or chroma
        # First try the splashURL. If that 404s..
        splashURL = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/{championRawID}/{skinRawID}.jpg"
        res = requests.get(splashURL)
        if res.status_code == 404:  # ..then it's a chroma
            chromaURL = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-chroma-images/{championRawID}/{skinRawID}.png"
            res = requests.get(chromaURL)
        if res.status_code != 200:
            raise ConnectionError(f"Error code {res.status_code} when getting art for {skinRawID}.")
        img = np.array(Image.open(BytesIO(res.content)))

        # Downsize image if it's too big.
        # 1200x700 is too big. 500x300 is not too big.
        n_pixels = np.shape(img)[0]*np.shape(img)[1]
        while n_pixels > 500000:
            img = img[::2,::2]
            n_pixels = np.shape(img)[0]*np.shape(img)[1]

        if np.shape(img)[2] == 4:  # then it's RGBA. convert to RGB.
            # strategy: all pixels with alpha < 255 are sent to blank white
            transparent_mask = img[:,:,3] < 255
            img[transparent_mask] = [255,255,255,255]
            img = img[:,:,0:3]
        return img


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
