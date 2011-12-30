#!/usr/bin/env python
"""TCP socket server for feeding requests into Rosie"""

import socket
import select
import os
from pubsub import pub

class TCPHandler:
	def __init__(self, rosie, port=2062):
		self.rosie = rosie
		self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.listener.bind(('', port))
		self.listener.listen(1)

		rosie.add_io_handler(self.listener,
					self.connection_handler)

	def connection_handler(self, fd, event):
		if fd == self.listener:
			(con,addr) = self.listener.accept()
			pub.sendMessage('TRACE.TCPSocket', msg=("Accepting connection from:" ,addr))
			con.setblocking(0)
			self.rosie.add_io_handler(con,
					self.request_handler)
			

	def request_handler(self, fd, event):
		data = fd.recv(4096)
		if not data: # No more data, we're done
			self.rosie.remove_io_handler(fd)
			fd.close()
		args = data.strip().split(' ')
		pub.sendMessage('TRACE.TCPSocket', msg=('Received: "%s"' % data ))
		if args[0] == 'X10':
			pub.sendMessage('SendX10', addr=args[1], command=args[2])
