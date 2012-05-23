#!/usr/bin/env python
"""Custom handler to respond to light levels"""

import select
import os
from pubsub import pub

class Light:
	def __init__(self, rosie):
		self.rosie = rosie
		self.last_level = 0;

		pub.subscribe(self.photo_handler, 'photo')

	def photo_handler(self, level):
		if (level >= 750 and self.last_level < 750):
			pub.sendMessage('SendX10', addr='L4', command='On')
			self.last_level = level
			return
		if (level < 750 and self.last_level >= 750):
			pub.sendMessage('SendX10', addr='L4', command='Off')
			self.last_level = level
			return

