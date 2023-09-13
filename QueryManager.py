"""
This class provides an abstraction for querying the Philips Hue Bridge.
This clsas does NOT provide an abstraction for querying the local game client or the Community Dragon. Those are
done directly through requests.get() in GameState.py.
"""

import urllib3
import requests
from time import sleep, time
from typing import Callable
from configparser import ConfigParser
import colorlib
import numpy as np
from scipy.optimize import fsolve
import threading
import logging



class QueryManager:
    def __init__(self, config: ConfigParser):
        logging.info("Starting QueryManager..")
        urllib3.disable_warnings()  # TODO figure out SSL stuff

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
            logging.error("Could not find a unique light group matching the configured id", group_objects, group_query)
        group = group_query[0]

        for child in group['children']:
            if child['rtype'] == 'device':
                deviceGet = self.get_resource(f"/device/{child['rid']}")
                lightGet = [device for device in deviceGet[0]["services"] if device['rtype'] == 'light']
                light_id = lightGet[0]['rid']
                child['rid'] = light_id
                child['rtype'] = 'light'
        self.light_ids = [child['rid'] for child in group['children']]
        logging.info("Started QueryManager")


    def get_light_states(self, light_ids=None):
        if light_ids is None:
            light_ids = self.light_ids

        states = {}
        for light_id in light_ids:
            state = self.get_resource(f"/light/{light_id}")[0]

            body = {
                "color": {
                    "xy": state["color"]["xy"]
                },
                "dimming": {
                    "brightness": state["dimming"]["brightness"]
                }
            }
            states[light_id] = body
        return states

    def apply_light_states(self, states: dict):
        for light_id in states.keys():
            state = states[light_id]
            self.put_resource(f"/light/{light_id}", json=state)


    def set_color(self, *light_ids, x: float = 0.31271, y: float = 0.32902,  # default white
                  duration_ms = 400, brightness=None, **kwargs):
        if len(light_ids) == 0:
            light_ids = self.light_ids
        json = {
            "color": self._color(x, y),
            "dynamics": {
                "duration": int(duration_ms)
            }
        }
        if brightness is not None:
            json["dimming"] = {"brightness": brightness}
        for light_id in light_ids:
            self.put_resource(f"/light/{light_id}", json=json, **kwargs)


    def rainbow(self, recall_scene_id: str, time_per_cycle = 6, cycles = 2):
        """
        Does a rainbow on each of the lights, then recalls a scene dynamically.
        return_to: the id of a scene to return to.
        """

        """OLD CODE, used to compute the hard-coded x-y points below
           #  colors                 R    Y    YG   BG   C    B    I    V    M
           hsv_gamut = np.array([[   0,  36,  72, 148, 180, 200, 252, 288, 324],
                                 [   1,   1,   1,   1,   1, 0.8, 0.5, 0.8, 0.8],
                                 [   1,   1,   1,   1,   1,   1,   1,   1,   1]])
           transition_coeffs =   [   1,   1,   1,   1,   1,   1,   1,   1,   1]
           
           # RGB is 0, 135, 257
           hsv_gamut = np.array([[   0,  125,  200, 300, 0],
                                 [   1,   1,    0.8, 0.5, 0.9],
                                 [   1,   1,    1,   1,   1]])
           transition_coeffs = np.array(
                                 [   1,   3,   2.5,   2,   2])
           transition_coeffs = transition_coeffs / np.mean(transition_coeffs)
           
           rgb_gamut = colorlib.hsv_to_rgb(hsv_gamut)
           xy_gamut = colorlib.rgb_to_xyb(rgb_gamut)
           x = xy_gamut[0]
           y = xy_gamut[1]
           n_points = len(x)
           """

        x = [0.64007440, 0.29887321, 0.20410905, 0.31840055, 0.62558534]
        y = [0.32997046, 0.59594318, 0.23778214, 0.20785135, 0.32992757]
        transition_coeffs = [1, 3, 2, 2, 2]
        scalar = len(transition_coeffs) / sum(transition_coeffs)
        transition_coeffs = [scalar * coeff for coeff in transition_coeffs]
        n_points = 5

        request_duration_s = time_per_cycle / n_points
        request_duration_ms = int(request_duration_s * 1000)

        class Device(threading.Thread):
            def __init__(self, queryman, light_id, barrier):
                self.queryman = queryman
                self.light_id = light_id
                self.barrier = barrier
                threading.Thread.__init__(self)

            def run(self):
                for cycle in range(cycles):
                    for point in range(n_points):
                        self.queryman.set_color(self.light_id,
                                                x=x[point],
                                                y=y[point],
                                                duration_ms=request_duration_ms*transition_coeffs[point])
                        self.barrier.wait()

        barrier = threading.Barrier(1 + len(self.light_ids), timeout=10)
        threads = [Device(self, light_id, barrier) for light_id in self.light_ids]
        for thread in threads:
            thread.start()

        for cycle in range(cycles):
            for point in range(n_points):
                sleep(request_duration_s*transition_coeffs[point])
                barrier.wait()
                barrier.reset()

        for thread in threads:
            thread.join()

        self.recall_dynamic_scene(recall_scene_id)


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
                        # "dimming": {  # TODO do we need "dimming"? ~~YES WE DO~~ NO WE DONT
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
            "speed": 0.75,
            "type": "scene"
        }

        res = self.post_resource(path="/scene", json=body)
        rid = res[0]['rid']
        return rid

    def recall_dynamic_scene(self, scene_id: str) -> None:
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

    def put_resource(self, path: str, json: dict, **kwargs):
        return self.__query_resource(path, requests.put, json=json, **kwargs)

    def delete_resource(self, path: str):
        return self.__query_resource(path, requests.delete)

    def __query_resource(self, path: str, request: Callable, json=None, **kwargs):
        """request should be a query function in lib requests"""
        request_url = self.base_request_url + path
        request_header = {"hue-application-key": self.user}
        logging.debug(f"Bridge Query. Path: {path}. Body: {json}")
        try:
            res = request(url=request_url,
                          headers=request_header,
                          json=json,
                          verify=False,  # TODO figure out SSL stuff
                          **kwargs)

            if res.status_code >= 300:
                raise ConnectionError
            return res.json()['data']
        except Exception as e:
            logging.error(e, request_url, request_header, json, kwargs)
            return None


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




# For testing the rainbow() function, so that it looks good.
if __name__ == "__main__":
    parser = ConfigParser()
    parser.read("config.ini")
    queryman = QueryManager(parser)


    # For rainbow()
    recall_scene_id = "d77ccf4c-93a5-4765-ad09-eeb61b14e315"
    queryman.rainbow(recall_scene_id=recall_scene_id)
    exit()


    # For HSV stuff
    recall_scene_id = "d77ccf4c-93a5-4765-ad09-eeb61b14e315"

    hsv_gamut = np.array([[0,120,240, 360],
                          [1,1,1, 1],
                          [1,1,1, 1]])
    points = 12
    points = points - 1  # must end where it starts, yeah?
    hsv_gamut = np.array([np.linspace(0,360,points),
                          np.repeat(1,points),
                          np.repeat(1,points)])
    hsv_gamut = hsv_gamut[:,0:-1]

    # corrections go here
    hsv_gamut = hsv_gamut[:,(0,1,2,3,4,5,6,7,8,9)]
    hsv_gamut[1,(6,7)] = 0.6
    hsv_gamut[0][6] = 200
    print(hsv_gamut)
    exit()
    rgb_gamut = colorlib.hsv_to_rgb(hsv_gamut)
    xy_gamut = colorlib.rgb_to_xyb(rgb_gamut)
    x = xy_gamut[0]
    y = xy_gamut[1]

    i = 0
    while True:
        print(hsv_gamut[0][i])
        tick = time()
        queryman.set_color(x=x[i], y=y[i],
        duration_ms=400)#, timeout=0.11)

        tock = time()
        print(tock - tick)
        i = (i + 1) % np.shape(hsv_gamut)[1]

    exit()


    queryman.recall_dynamic_scene(recall_scene_id)
    exit()





    # For hex one by one
    hex_gamut = [[0.6915, 0.3038],
                 [0.4308, 0.5019],
                 [0.17, 0.7],
                 [0.1616, 0.3737],
                 [0.1616, 0.1],
                 [0.42235, 0.17565]]


    # C
    queryman.set_color(x=hex_gamut[3][0], y=hex_gamut[3][1],
                       duration_ms=2000)
    sleep(3)
    # B
    queryman.set_color(x=hex_gamut[4][0], y=hex_gamut[4][1],
                       duration_ms=2000)
    sleep(3)
    # M
    queryman.set_color(x=hex_gamut[5][0], y=hex_gamut[5][1],
                       duration_ms=2000)
    sleep(3)
    # R
    queryman.set_color(x=hex_gamut[0][0], y=hex_gamut[0][1],
                       duration_ms=2000)
    exit()



    # use this to debug!
    light_id = queryman.light_ids[0]
    body = queryman.get_resource(f"/scene")
    data = body
    queryman.set_color(0.234, 0.1006)


    exit()  # breakpoint here