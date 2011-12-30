#!/usr/bin/env python
# Based on http://www.smarthome.com/manuals/2412sdevguide.pdf
# with help from http://www.madreporite.com/insteon/commands.htm

from serial import *
from struct import *
from time import sleep
from pubsub import pub

STX=0x02
ACK=0x06
NAK=0x15

PLMMessages = {
 0x50: {'desc': 'StandardMessage (9 bytes)', 'len': 11}
,0x51: {'desc': 'ExtendedMessage (23 bytes)', 'len': 25}
,0x52: {'desc': 'X10Received', 'len': 4}
,0x53: {'desc': 'AllLinkingCompleted', 'len': 10}
,0x54: {'desc': 'ButtonEvent', 'len': 3}
,0x55: {'desc': 'UserReset', 'len': 2}
,0x56: {'desc': 'AllLinkCleanupFailure', 'len': 7}
,0x57: {'desc': 'AllLinkRecord', 'len': 57}
,0x58: {'desc': 'AllLinkCleanupStatus', 'len': 3}
,0x60: {'desc': 'GetIMInfo', 'len': 9}

,0x63: {'desc': 'SendX10Ret', 'len': 5}
}

PLMCommands = {
 'GetIMInfo': 0x60
,'SendAllLink': 0x61
,'SendInsteonMessage': 0x62
,'SendX10': 0x63
,'StartAllLinking': 0x64
,'CancelAllLinking': 0x65
,'SethostDevCategory': 0x66
,'Reset': 0x67
,'SetActMessageByte': 0x68
,'GetFirstAllLinkRecord': 0x69
,'GetNextAllLinkRecord': 0x6a
,'SetIMConfiguration': 0x6b
,'GetAllLinkRecordForSender': 0x6c
,'LEDOn': 0x6d
,'LEDOff': 0x6e
,'ManageAllLinkRecord': 0x6f
,'SetNAKMessageByte': 0x70
,'SetACKMessageTypeBytes': 0x71
,'RFSleep': 0x72
,'GetIMConfiguration': 0x73
}

class X10():
	HouseCode = {
		 'A': 0x6
		,'B': 0xe
		,'C': 0x2
		,'D': 0xa
		,'E': 0x1
		,'F': 0x9
		,'G': 0x5
		,'H': 0xd
		,'I': 0x7
		,'J': 0xf
		,'K': 0x3
		,'L': 0xb
		,'M': 0x0
		,'N': 0x8
		,'O': 0x4
		,'P': 0xC
	}
	NibbleToHouseCode = {0: 'M', 1: 'E', 2: 'C', 3: 'K', 4: 'O', 5: 'G', 6: 'A', 7: 'I', 8: 'N', 9: 'F', 10: 'D', 11: 'L', 12: 'P', 13: 'H', 14: 'B', 15: 'J'}

	UnitCode = {
		 1: 0x6
		,2: 0xe
		,3: 0x2
		,4: 0xa
		,5: 0x1
		,6: 0x9
		,7: 0x5
		,8: 0xd
		,9: 0x7
		,10: 0xf
		,11: 0x3
		,12: 0xb
		,13: 0x0
		,14: 0x8
		,15: 0x4
		,16: 0xC
	}
	NibbleToUnitCode = {0: 13, 1: 5, 2: 3, 3: 11, 4: 15, 5: 7, 6: 1, 7: 9, 8: 14, 9: 6, 10: 4, 11: 12, 12: 16, 13: 8, 14: 2, 15: 10}

	Command = {
		 'AllOff': 0x6
		,'StatusOff': 0xa
		,'On': 0x2
		,'PresetDim': 0xa
		,'AllOn': 0x1
		,'HallACK': 0x9
		,'Bright': 0x5
		,'StatusOn': 0xd
		,'ExtendedCode': 0x7
		,'StatusRequest': 0xf
		,'Off': 0x3
		,'PresetDim': 0xb
		,'AllOff': 0x0
		,'HallRequest': 0x8
		,'Dim': 0x4
		,'ExtendedData': 0xC
	}
	NibbleToCommand = {0: 'AllOff', 1: 'AllOn', 2: 'On', 3: 'Off', 4: 'Dim', 5: 'Bright', 7: 'ExtendedCode', 8: 'HallRequest', 9: 'HallACK', 10: 'StatusOff', 11: 'PresetDim', 12: 'ExtendedData', 13: 'StatusOn', 15: 'StatusRequest'}

def hexdump(str):
	ret = ''
	for c in str:
		ret += '%02X ' % (ord(c))
	return ret

class InsteonHandler:
	"""Sends SendX10 and insteon events out to the world via the PLM
	Also, generates X10 & insteon messages from data received from the PLM
	"""
	def __init__(self, rosie, dev='/dev/ttyS0'):
		self.s = Serial(dev,
			 baudrate=19200,        #baudrate
			 bytesize=EIGHTBITS,    #number of databits
			 parity=PARITY_NONE,    #enable parity checking
			 stopbits=STOPBITS_ONE, #number of stopbits
			 timeout=2,             #set a timeout value, None for waiting forever
			 xonxoff=0,             #enable software flow control
			 rtscts=0,              #enable RTS/CTS flow control
		       )
		rosie.add_io_handler(self.s, self.input_handler)

		pub.subscribe(self.insteon_event_handler, 'insteon')
		pub.subscribe(self.sendX10_event_handler, 'SendX10')

	def sendX10_event_handler(self, addr, command):
		if command in X10.Command:
			self.SendX10(addr, command)

	def insteon_event_handler(self, addr, command):
		print "Got Insteon Event for", addr, command

	def input_handler(self, fd, event):
		if event == select.POLLIN:
			isSTX = self.s.read()
			if isSTX == chr(STX):
				cmd=self.s.read(1)
				data = self.s.read(PLMMessages[ord(cmd)]['len'] - 2)
				msg = chr(STX)+cmd+data
				print "< " + hexdump(msg) + self.decodemsg(msg)
			else:
				print "Not STX! (%02X)" % ord(isSTX)

	def SendCommand(self, command, data):
		msg = pack('BB', STX, PLMCommands[command]) + data
		print "> " + hexdump(msg) + self.decodemsg(msg)
		self.s.write(msg)

		# Wait for the ACK/NAK
		ret = self.s.read(PLMMessages[ord(msg[1])]['len'])
		print "< " + hexdump(ret) + self.decodemsg(ret),
		if ord(ret[-1]) != ACK:
			print "NAK"
		else:
			print "ACK"

	def SendX10(self, addr, cmd):
		"""X10 commands get sent as two PLM command
		The first sends the address, the second the command, both include the house code
		"""
		house = addr[0]
		unit = int(addr[1])
		housenibble = X10.HouseCode[house] << 4
		data = pack('BB', housenibble | X10.UnitCode[unit], 0x00)
		self.SendCommand('SendX10', data )

		sleep(0.500)

		data = pack('BB', housenibble | X10.Command[cmd], 0x80)
		self.SendCommand('SendX10', data )
		sleep(0.500)

	def decodemsg(self, msg):
		if len(msg) < 2:
			return '' # Bail
		cmd=ord(msg[1])
		if cmd==0x63 or cmd==0x52:
			ret = "X10 "
			housecode = (ord(msg[2]) & 0xf0) >> 4
			lower = ord(msg[2]) & 0x0f
			flag = ord(msg[3])
			if flag == 0x80:
				ret += X10.NibbleToCommand[lower]
			else:
				ret += X10.NibbleToHouseCode[housecode]
				ret += str(X10.NibbleToUnitCode[lower])
			return ret
		if cmd==0x50 or cmd==0x51:
			(fromaddr, toaddr, flags, cmd1, cmd2) = unpack('3s3sccc', msg[2:])
			ret  = "Insteon Std "
			ret += "From:" + hexdump(fromaddr)
			ret += "To:" + hexdump(toaddr)
			ret += "Flags:" + hexdump(flags)
			ret += "Cmd:" + hexdump(cmd1+cmd2)
			if cmd==0x51:
				ret += "UserData:" + hexdump(msg[11:14])
			return ret
			
		if cmd in PLMMessages:
			return PLMMessages[cmd]['desc']
		return 'donno'

	def decodeloop(self):
		while (True):
			isSTX = self.s.read(1)
			if len(isSTX) == 0:
				continue
			if isSTX == chr(STX):
				cmd=self.s.read(1)
				data = self.s.read(PLMMessages[ord(cmd)]['len'] - 2)
				msg = chr(STX)+cmd+data
				print "< " + hexdump(msg) + self.decodemsg(msg)
			else:
				print "Not STX! (%02X)" % ord(isSTX)
		

