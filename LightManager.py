from phue import Bridge
from time import sleep
import requests


class LightManager:
	# constants
	self.WHITE = [0.35,0.35]
	self.DEFAULT = [0.4,0.2] # magenta-purpleish

	def __init__(self, active_IDs, ip, username):
		# INPUT params:
		# light_ids to be managed, as stored on Bridge
		# ip of Bridge
		# username to access Bridge API

		self.active_IDs = active_IDs
		self.ip = ip
		self.username = username

		# To interface with lights through phue.py
		self.lights = Bridge(ip).get_light_objects('id')

		# To interface with lights through http
		base_address = '/'.join(['http:/',
			ip,
			"api",
			username,
			"lights"])
		# a dictionary containing each light's http address from which to query
		self.address = {ID: '/'.join([base_address, str(ID)]) for ID in active_IDs}

		# for rainbow()
		self.gamut_vertices = {}
		for ID in active_IDs:
			self.gamut_vertices[ID] = requests.get(address[ID]).json()['capabilities']['control']['colorgamut']


	def rainbow(self, time_per_cycle=2, cycles=1):
		# Store initial value
		init_vals = {ID: requests.get(self.address[ID]).json()['state']['xy'] for ID in self.active_IDs}

		for cycle in range(cycles):
			# Rainbow by transitioning to all three corners of gamut
			for i in range(3):
				for ID in self.active_IDs:
					lights[ID].transitiontime = time_per_cycle*10/3
					lights[ID].xy=self.gamut_vertices[ID][i]
				sleep(time_per_cycle/3)
	
		# Return to initial value
		for ID in self.active_IDs:
			lights[ID].transitiontime=40
			lights[ID].xy = init_vals[ID]


	def apply_state(self, state):
		# state should be a dictionary {lightid: [x1, y1], ...}
		# lightid may be integer or string (e.g. 3 or '3')
		for ID in state:
			intID = int(ID)
			if intID in self.active_IDs:
				lights[intID].xy = state[ID]


	def apply_color(self, xy=self.DEFAULT):
		for ID in self.active_IDs:
			lights[ID].xy = xy