from matplotlib import pyplot as plt
from configparser import ConfigParser
from QueryManager import QueryManager
import model
from time import time
from GameState import GameManager
from colorlib import *

config = ConfigParser()
config.read('../config.ini')
queryman = QueryManager(config)


# Teemo 18, 25, 27 are pretty
# Seraphine 15 is pretty
#
# Morgana 26, Elise 0 are hard because they're dark
# Aatrox 0 is hard because glowy

#championNames = ["Elise", "Ashe", "Pyke", "Cho'Gath", "Riven", "Seraphine", "Veigar", "Warwick", "Aatrox"]
championNames = ["Ahri","Akali","Akshan","Alistar","Amumu","Anivia","Annie","Aphelios","Ashe","Aurelion Sol","Azir","Bard","Bel'Veth","Blitzcrank","Brand","Braum","Caitlyn","Camille","Cassiopeia","Cho'Gath","Corki","Darius","Diana","Dr. Mundo","Draven","Ekko","Elise","Evelynn","Ezreal","Fiddlesticks","Fiora","Fizz","Galio","Gangplank","Garen","Gnar","Gragas","Graves","Gwen","Hecarim","Heimerdinger","Illaoi","Irelia","Ivern","Janna","Jarvan IV","Jax","Jayce","Jhin","Jinx","Kai'Sa","Kalista","Karma","Karthus","Kassadin","Katarina","Kayle","Kayn","Kennen","Kha'Zix","Kindred","Kled","Kog'Maw","LeBlanc","Lee Sin","Leona","Lillia","Lissandra","Lucian","Lulu","Lux","Malphite","Malzahar","Maokai","Master Yi","Miss Fortune","Mordekaiser","Morgana","Nami","Nasus","Nautilus","Neeko","Nidalee","Nocturne","Nunu & Willump","Olaf","Orianna","Ornn","Pantheon","Poppy","Pyke","Qiyana","Quinn","Rakan","Rammus","Rek'Sai","Rell","Renata Glasc","Renekton","Rengar","Riven","Rumble","Ryze","Samira","Sejuani","Senna","Seraphine","Sett","Shaco","Shen","Shyvana","Singed","Sion","Sivir","Skarner","Sona","Soraka","Swain","Sylas","Syndra","Tahm Kench","Taliyah","Talon","Taric","Teemo","Thresh","Tristana","Trundle","Tryndamere","Twisted Fate","Twitch","Udyr","Urgot","Varus","Vayne","Veigar","Vel'Koz","Vex","Vi","Viego","Viktor","Vladimir","Volibear","Warwick","Wukong","Xayah","Xerath","Xin Zhao","Yasuo","Yone","Yorick","Yuumi","Zac","Zed","Zeri","Ziggs","Zilean","Zoe","Zyra"]
#championName = "Riven"
championNames = championNames[8:]
skinID = 0

#championNames=["Ashe"]
skinID=0

for championName in championNames:

    (championRawID, skinRawID) = GameManager.get_community_dragon_info(championName, skinID)
    img = GameManager.get_champion_img(championRawID, skinRawID)

    """
    dim, pixels_rgb = flatten_image(img)
    pixels_hsv = rgb_to_hsv(pixels_rgb)
    for i in range(3):
        plt.subplot(3,1,i+1)
        plt.hist(pixels_hsv[i])
    #plt.show()
    
    
    print("Per: [" + "       ".join(["0.10","0.25","0.50","0.75","0.90"]) + "]")
    print("Sat:", np.percentile(pixels_hsv[1], [10,25,50,75,90]))
    print("Val:", np.percentile(pixels_hsv[2], [10,25,50,75,90]))
    """
    scene_name = f"{championName}_{skinID}"
    scene_id = model.img_to_scene(img, scene_name, queryman=queryman, debugging=True)


#queryman.recall_dynamic_scene(scene_id)
    queryman.delete_scene(scene_id)
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()
    plt.show()
#queryman.set_color()

