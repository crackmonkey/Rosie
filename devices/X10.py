#!/usr/bin/env python
"""X10 power control device"""

import power
from pubsub import pub

class X10(power.PowerDevice):
	dimmable = False
	addr = None
	caps = ['on', 'off', 'status']

	def __init__(self, name, addr, dimmable):
		super(X10,self).__init__(name)
		self.addr = addr
		if dimmable:
			self.caps.append('dim')
		pub.subscribe(self.event_handler, 'X10.%s' % addr)

	def event_handler(self, command, topic=pub.AUTO_TOPIC):
		print self.name,"Got",topic,command

	def capabilities(self):
		return caps

	def on(self):
		pub.sendMessage('SendX10', addr=self.addr, command='On')

	def off(self):
		pub.sendMessage('SendX10', addr=self.addr, command='Off')

	def dim(self, pct):
		pub.sendMessage('SendX10', addr=self.addr, command='Dim:%i'%pct)

