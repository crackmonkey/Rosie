#!/usr/bin/env python
import sys
import select

sys.path.append('PyPubSub-3.1.2-py2.6.egg')
from pubsub import pub

from handlers.arduino import Arduino
from handlers.light import Light
from handlers.zabbixpush import ZabbixPush
import handlers.insteon
import handlers.tcpsocket
from devices.X10 import X10

def tracelogger(topic=pub.AUTO_TOPIC, **kwargs):
	"""Dump what pubsub is doing"""
	print "TRACE:",topic,kwargs

def stdinhandler(fd, event):
	sys.stdin.read(1)
	pub.sendMessage('SendX10', addr='L5', command='On')

class Rosie():
	FDs = {} # By FDs I really mean file-like objects
	timers = []

	def __init__(self):
		self.poller = select.poll()
		pub.subscribe(tracelogger, pub.ALL_TOPICS)

		pub.sendMessage('lifecycle', msg='Starting up')

		# Register modules
		handlers.insteon.InsteonHandler(self, dev='/dev/ttyS0')
		handlers.tcpsocket.TCPHandler(self, port=2062)
		Arduino(self,dev='/dev/ttyACM0')
		holdme = Light(self)
		holdme2 = ZabbixPush(self)

		testdev = X10('fishtank', 'L4', False)


		#self.add_io_handler(sys.stdin.fileno(), stdinhandler)

		# load configs?

		# main loop
		pub.sendMessage('lifecycle', msg='Starting main loop')
		while (True):
			try:
				active=self.poller.poll()
				for (fd, event) in active:
					# Call the FD event handler
					for i in self.FDs:
						if i.fileno() == fd:
							self.FDs[i](i, event)
							break
			except KeyboardInterrupt:
				break

		pub.sendMessage('lifecycle', msg='Quiting')

	def add_io_handler(self, fd, handler):
		"""Register a function(fd, data) to be called when poll()
		detects input.
		"""
		self.poller.register(fd, select.POLLIN)
		self.FDs[fd] = handler

	def remove_io_handler(self, fd):
		"""Unregister a file descriptor from polling"""
		self.poller.unregister(fd)
		del self.FDs[fd]


if __name__ == '__main__':
	dog = Rosie()
