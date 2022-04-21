import requests
from typing import Callable
from configparser import ConfigParser

class QueryManager:
    def __init__(self, config: ConfigParser):
        # store these for resource requesting methods
        self.user = config["Philips Hue"]["user"]
        self.key = config["Philips Hue"]['key']
        self.base_request_url = f"https://{config['Philips Hue']['bridge_address']}/clip/v2/resource"

        # get the light_ids for the given group
        self.group_type = config["Philips Hue"]['group_type']
        self.group_id = config["Philips Hue"]['group_id']
        group_objects = self.get_resource(f"/{self.group_type}")
        group_query = [group for group in group_objects if group['id'] == self.group_id]
        if len(group_query) != 1:
            self.__log_error(Exception("Could not find a unique group matching the configured id."))
        group = group_query[0]
        self.lights = group['children']
        for child in group['children']:
            if child['rtype'] == 'device':
                deviceGet = self.get_resource(f"/device/{child['rid']}")
                lightGet = [device for device in deviceGet[0]["services"] if device['rtype'] == 'light']
                light_id = lightGet[0]['rid']
                child['rid'] = light_id
                child['rtype'] = 'light'


        self.light_ids = [child['rid'] for child in group['children']]

    def set_color(self, x: float = 0.31271, y: float = 0.32902):
        json = {
            "color": self._color(x, y)
        }
        for light_id in self.light_ids:
            self.put_resource(f"/light/{light_id}", json=json)

    def post_scene(self, sceneName: str, x: list, y: list) -> str:
        """
        Truncates the parameters to meet the following conditions:
            skinName: 1 <= len(skinName) <= 32
            x: 2 <= len(x) <= 9
            y: 2 <= len(y) <= 9
        Returns the scene_id
        """

        # First, iterate through the lights and choose a starting color for each
        sceneName = sceneName[:32]
        base_x = []
        base_y = []
        i_light = 0
        i_color = 0
        while i_light < len(self.light_ids):
            base_x.append(x[i_color])
            base_y.append(y[i_color])
            i_light = i_light + 1
            i_color = (i_color + 1) % len(x)

        body = {
            "metadata": {
                "name": sceneName
            },
            "group": {
                "rid": self.group_id,
                "rtype": self.group_type
            },
            "actions": [
                {
                    "action": {
                        "on": {
                            "on": True
                        },
                        "color": self._color(base_x[i], base_y[i]),
                        # "dimming": {  # TODO do we need "dimming"?
                        #     "brightness": 100
                        # },
                        "dynamics": {  # TODO is this useful?
                            "duration": 400
                        }
                    },
                    "target": {
                        "rid": light_id,
                        "rtype": "light"
                    }
                } for i, light_id in enumerate(self.light_ids)
            ],
            "palette": {
                "color": [
                    {
                        "color": self._color(x[i], y[i]),
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
            "speed": 0.8,
            "type": "scene"
        }

        res = self.post_resource(path="/scene", json=body)
        rid = res[0]['rid']
        return rid

    def recall_scene(self, scene_id: str) -> None:
        body = {
            "recall": {
                "action": "dynamic_palette"
            }
        }
        self.put_resource(f"/scene/{scene_id}", json=body)  # TODO what if you recall a scene that doesn't exist?

    def delete_scene(self, scene_id: str) -> None:
        self.delete_resource(f"/scene/{scene_id}")


    def get_resource(self, path: str):
        return self.__query_resource(path, requests.get)

    def post_resource(self, path: str, json: dict):
        return self.__query_resource(path, requests.post, json=json)

    def put_resource(self, path: str, json: dict):
        return self.__query_resource(path, requests.put, json=json)

    def delete_resource(self, path: str):
        return self.__query_resource(path, requests.delete)

    def __query_resource(self, path: str, request: Callable, json=None):
        """request should be a query function in lib requests"""
        request_url = self.base_request_url + path
        request_header = {"hue-application-key": self.user}
        try:
            res = request(url=request_url,
                          headers=request_header,
                          json=json,
                          verify=False) # TODO figure out SSL stuff
            if res.status_code >= 300:
                raise ConnectionError
            return res.json()['data']
        except Exception as e:
            self.__log_error(e)
            return None



    def __log_error(self, e: Exception):
        """
        TODO implement actual logging.
        """
        print(e)


    def _color(self, x, y):
        """
        Return a JSON object containing {"xy": {"x": x, "y": y}}
        """
        return {
            "xy": {
                "x": x,
                "y": y
            }
        }
