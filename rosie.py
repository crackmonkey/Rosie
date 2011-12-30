#!/usr/bin/env python
import sys
import select

sys.path.append('PyPubSub-3.1.2-py2.6.egg')
from pubsub import pub

import handlers.insteon

def tracelogger(topic=pub.AUTO_TOPIC, **kwargs):
	"""Dump what pubsub is doing"""
	print "TRACE:",topic,kwargs

def stdinhandler(fd, event):
	sys.stdin.read(1)
	pub.sendMessage('SendX10', addr='L5', command='On')

class Diety():
	FDs = {}
	timers = []

	def __init__(self):
		self.poller = select.poll()
		pub.subscribe(tracelogger, pub.ALL_TOPICS)

		pub.sendMessage('lifecycle', msg='Starting up')

		# Register modules
		handlers.insteon.InsteonHandler(self, '/dev/ttyS0')
		self.add_io_handler(sys.stdin.fileno(), stdinhandler)

		# load configs?

		# main loop
		pub.sendMessage('lifecycle', msg='Starting main loop')
		while (True):
			try:
				active=self.poller.poll()
				for (fd, event) in active:
					# Call the FD event handler
					self.FDs[fd](fd, event)
			except KeyboardInterrupt:
				break

		pub.sendMessage('lifecycle', msg='Quiting')

	def add_io_handler(self, fd, handler):
		"""Register a function(fd, data) to be called when poll()
		detects input.
		"""
		self.poller.register(fd, select.POLLIN)
		self.FDs[fd] = handler

	def remove_io_handler(self, fd, handler):
		"""Unregister a file descriptor from polling"""
		self.poller.unregister(fd)
		del self.FDs[fd]


if __name__ == '__main__':
	dog = Diety()
