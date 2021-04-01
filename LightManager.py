from phue import Bridge
from time import sleep
import requests
import db_manager

class LightManager:
	# constants
	WHITE = [0.347,0.357]
	DEFAULT = [0.22,0.45] # ruined-king green
	BLUE = [0.156,0.145]
	RED = [0.678,0.3018]

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

		# TODO user can't adjust brightness themselves without a transition mucking it
		self.brightness = {ID: self.lights[ID].brightness for ID in active_IDs}

		# for rainbow()
		self.gamut_vertices = {}
		for ID in active_IDs:
			self.gamut_vertices[ID] = requests.get(self.address[ID]).json()['capabilities']['control']['colorgamut']


	def rainbow(self, time_per_cycle=2, cycles=1):
		# Store initial value
		init_vals = {ID: requests.get(self.address[ID]).json()['state']['xy'] for ID in self.active_IDs}

		for cycle in range(cycles):
			# Rainbow by transitioning to all three corners of gamut
			for i in range(3):
				for ID in self.active_IDs:
					self.lights[ID].transitiontime = time_per_cycle*10/3
					self.lights[ID].xy=self.gamut_vertices[ID][i]
				sleep(time_per_cycle/3)
	
		# Return to initial value
		for ID in self.active_IDs:
			self.lights[ID].transitiontime=40
			self.lights[ID].xy = init_vals[ID]

	# Returns a JSON string for each dictionary's xy
	# e.g. '{"3":[0.3,0.3], "4":[0.4,0.4]}'
	# for good input into db_manager.set_state()
	def get_state(self):
		# We need double quotes around the keys
		result = {str(ID): self.lights[ID].xy for ID in self.active_IDs}
		return str(result).replace('\'', '\"')


	def apply_state(self, state, transitiontime=4, brightness_coeff=1):
		# state should be a dictionary {lightid: [x1, y1], ...}
		# lightid may be integer or string (e.g. 3 or '3') # TODO this introduces problems on .xy and .brightness
		# transitiontime is an integer in unit deciseconds.
		for ID in state:
			intID = int(ID)
			if intID in self.active_IDs:
				self.lights[intID].transitiontime = transitiontime
				self.lights[intID].xy = state[ID]
				self.lights[intID].brightness = int(brightness_coeff*self.brightness[intID])

	def apply_color(self, xy=DEFAULT, transitiontime=4, brightness_coeff=1):
		for ID in self.active_IDs:
			self.lights[ID].transitiontime = transitiontime
			self.lights[ID].xy = xy
			# TODO user can't adjust brightness themselves without a transition mucking it
			self.lights[ID].brightness = int(brightness_coeff*self.brightness[ID])