#!/usr/bin/env python
"""Base class for all power-type devices
"""

class PowerDevice(object):
	name = ''
	def __init__(self, name):
		self.name = name
		pass

	def on(self):
		pass

	def off(self):
		pass

	def dim(self):
		pass

	def can_dim(self):
		return None	

	def status(self):
		return None	

	def capabilities(self):
		"""Return a list of valid commands"""
		return []

