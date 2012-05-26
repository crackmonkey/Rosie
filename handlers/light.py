#!/usr/bin/env python
"""Custom handler to respond to light levels"""

import select
import os
from pubsub import pub

class Light:
	def __init__(self, rosie):
		self.rosie = rosie
		self.last_level = 0;
		self.ison = False

		pub.subscribe(self.photo_handler, 'photo')

	def photo_handler(self, level):
		if (level >= 750 and not self.ison):
			pub.sendMessage('SendX10', addr='L4', command='On')
			self.ison = True
			return
		if (level < 650 and self.ison):
			pub.sendMessage('SendX10', addr='L4', command='Off')
			self.ison = False
			return

