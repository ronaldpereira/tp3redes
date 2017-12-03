import sys
import socket

class ServentInfo:
	def __init__(self):
		self.ip = '127.0.0.1'
		self.ipBinary = []
		self.ipBinaryConstructor()
		self.port = int(sys.argv[1])
		self.keyDictionary = {}
		self.keyDictionaryConstructor(sys.argv[2])
		print(self.keyDictionary)
		self.serventListConstructor(sys.argv[3])
		self.receivedMessagesList = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Option to reuse the socket address to stop giving the error: Adress is already being used when running the program multiple times
		self.sock.bind((self.ip, self.port))

	def ipBinaryConstructor(self):
		self.ipBinary.append((127).to_bytes(1, 'big'))
		self.ipBinary.append((0).to_bytes(1, 'big'))
		self.ipBinary.append((0).to_bytes(1, 'big'))
		self.ipBinary.append((1).to_bytes(1, 'big'))

	def keyDictionaryConstructor(self, inputFile):
		file = open(inputFile, 'r')
		keys = file.readlines()

		for key in keys:
			if key[0] != '#':
				key = key.split()
				self.keyDictionary[key[0]] = str.join(' ',(key[1:]))

	def serventListConstructor(self, servents):
		command = "[('"
		command += servents[1:].replace('[',"),('").replace(']','').replace(':',"',")
		command += ')]'
		self.serventList = eval(command)

	def checkMessageIsNew(self, recvMsg):
		for savedMsg in self.receivedMessagesList:
			if savedMsg[0] == recvMsg[8:14] and savedMsg[1] == recvMsg[4:8]:
				print('Message already received:', recvMsg)
				return False

		self.receivedMessagesList.append((recvMsg[8:14],recvMsg[4:8]))
		return True

class Message:
	def recvKeyReq(servent, recvMsg):
		keyFloodMsg = (7).to_bytes(2, 'big')
		keyFloodMsg += (3).to_bytes(2, 'big')
		keyFloodMsg += recvMsg[2:6]
		keyFloodMsg += servent.ipBinary[0]
		keyFloodMsg += servent.ipBinary[1]
		keyFloodMsg += servent.ipBinary[2]
		keyFloodMsg += servent.ipBinary[3]
		keyFloodMsg += (servent.port).to_bytes(2, 'big')
		keyFloodMsg += recvMsg[6:]

		print(keyFloodMsg)

		print(recvMsg[6:])
		if recvMsg[6:].decode() in servent.keyDictionary:
			Message.sendRespFromReq(servent, recvMsg)

		if servent.checkMessageIsNew(keyFloodMsg):
			Message.sendMessageToServentList(servent, keyFloodMsg)

	def recvTopoReq(servent, recvMsg):
		topoFloodMsg = (8).to_bytes(2, 'big')
		topoFloodMsg += (3).to_bytes(2, 'big')
		topoFloodMsg += recvMsg[2:6]
		topoFloodMsg += servent.ipBinary[0]
		topoFloodMsg += servent.ipBinary[1]
		topoFloodMsg += servent.ipBinary[2]
		topoFloodMsg += servent.ipBinary[3]
		topoFloodMsg += (servent.port).to_bytes(2, 'big')
		topoFloodMsg += (servent.ip).encode('ascii')
		topoFloodMsg += ':'.encode('ascii')
		topoFloodMsg += (str(servent.port)).encode('ascii')

		print(topoFloodMsg)

		if servent.checkMessageIsNew(topoFloodMsg):
			Message.sendMessageToServentList(servent, topoFloodMsg)

	def recvKeyFlood(servent, recvMsg):
		if recvMsg[14:] in servent.keyDictionary:
			print(recvMsg[14:])
			Message.sendResp(servent, recvMsg)

		keyFloodMsg = Message.decrementTTL(recvMsg)

		Message.sendMessageToServentList(servent, keyFloodMsg)


	def recvTopoFlood(servent, recvMsg):
		pass

	def sendMessageToServentList(servent, message):
		for serv in servent.serventList:
			servent.sock.sendto(message, (serv[0], serv[1]))

	def sendRespFromReq(servent, recvMsg):
		newMessage = (9).to_bytes(2, 'big')
		newMessage += recvMsg[2:6]
		newMessage += servent.keyDictionary[recvMsg[6:].decode()].encode('ascii')

		print(newMessage)
		print((servent.ip, servent.port))

		servent.sock.sendto(newMessage, (servent.ip, servent.port))

	def decrementTTL(message):
		ttlValue = int.from_bytes(message[2:4], 'big')
		print(ttlValue)
		ttlValue -= 1
		newMessage = message[0:2]
		newMessage += ttlValue.to_bytes(2, 'big')
		newMessage += message[4:]

		return newMessage


servent = ServentInfo()

while 1:
	recvMsg = servent.sock.recvfrom(414)[0] # 2 (message type size) + 2 (TTL size) + 4 (sequence number size) + 4 (IP origin size) + 2 (port origin size) + 400 (info or key size)
	print(recvMsg)

	if recvMsg[0:2] == (5).to_bytes(2, 'big'):
		Message.recvKeyReq(servent, recvMsg)

	elif recvMsg[0:2] == (6).to_bytes(2, 'big'):
		Message.recvTopoReq(servent, recvMsg)

	elif recvMsg[0:2] == (7).to_bytes(2, 'big'):
		if servent.checkMessageIsNew(servent, recvMsg):
			Message.recvKeyFlood(servent, recvMsg)

	elif recvMsg[0:2] == (8).to_bytes(2, 'big'):
		if servent.checkMessageIsNew(recvMsg):
			Message.recvTopoFlood(servent, recvMsg)

	print('')