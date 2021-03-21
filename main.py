# On first run, you will have to press your Philips Bridge
# button and start the script within 30 seconds (unless
# you've used phue.Bridge before).

from phue import Bridge
from time import sleep
import sqlite3
import requests


## parameters
# TODO store these and load from config.txt
ip = "10.0.0.52"
active_IDs = [3,4,5]
username = "t9EuSmHFC2o7bTtt5Lyq5eUMKNU0otLLN4nHE9wO"

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

rainbow(active_IDs)

## League API address
#response = requests.get("​https://127.0.0.1:2999/liveclientdata/allgamedata/")
#print(response.json())