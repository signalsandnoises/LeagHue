import requests
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')
hueSection = config['Philips Hue']
address = hueSection['bridgeaddress']
user = hueSection['user']
key = hueSection['key']
activeLights = hueSection['lights'].split(",")


base_request_url = f"https://{address}/clip/v2/resource"




# TODO implement actual logging.
def log_error(e: Exception):
    print(e)


def color(x, y):
    return {
        "xy": {
            "x": x,
            "y": y
        }
    }


def get_resource(path: str = ""):
    request_url = base_request_url + path
    res = None
    request_header = {"hue-application-key": user}
    try:
        res = requests.get(url=request_url,
                           headers=request_header,
                           verify=False)
        if res.status_code != 200: raise ConnectionError
        return res.json()
    except Exception as e:
        log_error(e)
        return None


def put_resource(path: str = "", json: dict = {}):
    request_url = base_request_url + path
    res = None
    request_header = {"hue-application-key": user}
    try:
        res = requests.put(url=request_url,
                           headers=request_header,
                           json=json,
                           verify=False)
        if res.status_code != 200: raise ConnectionError
        return res.json()
    except Exception as e:
        log_error(e)
        return None


def post_resource(path: str = "", json: dict = {}):
    request_url = base_request_url + path
    res = None
    request_header = {"hue-application-key": user}
    try:
        res = requests.post(url=request_url,
                            headers=request_header,
                            json=json,
                            verify=False)
        if res.status_code >= 300: raise ConnectionError
        return res.json()
    except Exception as e:
        log_error(e)
        return None


def query_light(light: str = "", json: dict = None) -> dict:
    """Usage:
    query_light(light=lightOne, json=body)
    """
    path = f"/light/{light}"
    if json == None:
        return get_resource(path=path)
    else:
        put_resource(path=path, json=json)
        return None


print(query_light(activeLights[0]))


def set_color(*lights, x: float, y: float):
    """Usage:
    set_color(lightOne, x=0.2, y=0.3)
    set_color(lightOne, lightTwo, x=0.2, y=0.3)
    set_color(*setOfLights, x=0.2, y=0.3)
    """
    body = {"color": color(x,y)}
    for light in lights:
        query_light(light=light, json=body)


#set_color(*activeLights, x=0.2, y=0.3)

body = {
    "effects": {
        "effect": "fire"
    }
}


#for light in activeLights:
#    query_light(light=light, json=body)
#foo = query_light(activeLights[0])


def post_scene(zone_id: str, lights: tuple, sceneName: str, x: list, y: list) -> str:
    """
    skinName: 1 <= len(skinName) <= 32
    Returns the scene_id
    """
    # Iterate through the lights and choose a default color
    sceneName = sceneName[:32]
    base_x = []
    base_y = []
    i_light = 0
    i_color = 0
    while i_light < len(lights):
        base_x.append(x[i_color])
        base_y.append(y[i_color])
        i_light = i_light + 1
        i_color = (i_color + 1) % len(x)

    body = {
        "metadata": {
            "name": sceneName
        },
        "group": {
            "rid": zone_id,
            "rtype": "zone"
        },
        "actions": [
            {
                "action": {
                    "on": {
                        "on": True
                    },
                    "color": color(base_x[i], base_y[i]),
                    "dynamics": {  # TODO is this useful?
                        "duration": 1000
                    } # TODO do we need "dimming": {100} ?
                },
                "target": {
                    "rid": light,
                    "rtype": "light"
                }
            } for i, light in enumerate(lights)
        ],
        "palette": {
            "color": [
                {
                    "color": color(x[i], y[i]),
                    "dimming": {
                        "brightness": 100  # TODO make this an actual thing by color
                    }
                } for i in range(len(x))
            ],
            "color_temperature": [],
            "dimming": [
                {
                    "brightness": 100  # TODO figure out if this needs to be anything
                }
            ]
        },
        "speed": 0.5,
        "type": "scene"
    }

    res = post_resource(path="/scene", json=body)
    rid = None
    try:
        rid = res['data'][0]['rid']
        return rid
    except Exception as e:
        log_error(e)
        return None

def recall_scene(scene_id: str) -> None:
    body = {
        "recall": {
            "action": "dynamic_palette"
        }
    }
    put_resource(f"/scene/{scene_id}", json=body)

def debug_resource(resource: str = ""):
    info_dict = get_resource(resource)["data"]
    info_str = json.dumps(info_dict, indent=4)
    return info_dict, info_str

print()

info_dict, info_str = debug_resource(f"/scene")
print()

zone_id = "008dc287-b0aa-4b7e-a4d2-af9f36850e11"  # from resource/zone["id"],  not from resource/zone["services"][0]["rid"]
scene_id = post_scene(zone_id, lights=activeLights, sceneName="Test Skin Programmatic", x=[0.2, 0.3, 0.4], y=[0.2, 0.2, 0.25])
recall_scene(scene_id)


info_dict, info_str = debug_resource(f"/scene")
print()



# League constants
patch = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
data_dragon_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/"

