#!/usr/bin/env python
"""Custom handler to shove data over to Zabbix"""

from pubsub import pub
import json
from socket import *

class ZabbixPush:
	def __init__(self, rosie):
		self.rosie = rosie
		self.last_level = 0;

		pub.subscribe(self.photo_handler, 'photo')
		pub.subscribe(self.temp_handler, 'temp1')
		pub.subscribe(self.humidity_handler, 'RH')

	def photo_handler(self, level):
		self.zabbix_push('photo', level)
	def humidity_handler(self, humidity):
		self.zabbix_push('humidity', humidity)
	def temp_handler(self, tempC, tempF):
		self.zabbix_push('temp', tempF)

	def zabbix_push(self, key, val):
		# The Zabbix JSON parser is picky, so we have to build the
		# JSON by hand instead of letting the JSON module do it
		injson = '{"request":"sender data",\
	"data":[\
		{\
			"host":"silentbob",\
			"key":"%s",\
			"value":"%s"}]}' % (key, val)

		#pub.sendMessage('zabbix', msg=injson)
	
		try:	
			s = socket(AF_INET, SOCK_STREAM)
			s.settimeout(10)
			s.connect(('hmcgregor01.biggeeks.org', 10051))
			s.send("ZBXD\x01")
			datalen = '%08x' % len(injson)
			datalen = datalen[6:8] + datalen[4:6] + datalen[2:4] + datalen[0:2]
			s.send(datalen)
			s.send(injson)
			#pub.sendMessage('zabbix', msg=s.recv(1024))
			s.close()
		except timeout:
			#nevermind
			pass

