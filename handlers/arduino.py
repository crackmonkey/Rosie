#!/usr/bin/env python
"""Handle my custom Arduino multi-sensor"""

import select
import os
from pubsub import pub
from serial import *

class Arduino:
	def __init__(self, rosie, dev):
		self.rosie = rosie
		self.last_values = {}

                self.s = Serial(dev,
                         baudrate=9600,        #baudrate
                         bytesize=EIGHTBITS,    #number of databits
                         parity=PARITY_NONE,    #enable parity checking
                         stopbits=STOPBITS_ONE, #number of stopbits
                         timeout=2,             #set a timeout value, None for waiting forever
                         xonxoff=0,             #enable software flow control
                         rtscts=0,              #enable RTS/CTS flow control
                       )
                rosie.add_io_handler(self.s, self.input_handler)


	def input_handler(self, fd, event):
		for ln in self.s:
			(key,val) = ln.split(':', 1)
			if (not self.last_values.has_key(key)):
				 self.last_values[key] = 0;
			if (val == self.last_values[key]):
				continue # nevermind
			
			if (key == 'photo'):
				pub.sendMessage(key, level=int(val))
			if (key == 'RH'):
				val = round(float(val),1)
				pub.sendMessage(key, humidity=val)
			if (key.startswith('temp')):
				pub.sendMessage(key, \
					tempC=float(val),
					tempF=float(val)*(9.0/5.0)+32
					)

			self.last_values[key] = val
		

