import sys
import struct
import socket

class ClientInfo:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = int(port)
		self.seqNum = 0
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class Message:
	def keyReq(client, message):
		try:
			datagram = (5).to_bytes(2, 'big')
			datagram += (client.seqNum).to_bytes(4, 'big')
			datagram += message[0:400].encode('ascii')

			print(datagram)

			client.sock.sendto(datagram, (client.ip, client.port))
			client.seqNum += 1

			client.sock.settimeout(4)

			resp = client.sock.recvfrom(406) # 2 (message type size) + 4 (sequence number size) + 400 (info or key size)

		except socket.timeout:

			try:
				datagram = (5).to_bytes(2, 'big')
				datagram += (client.seqNum).to_bytes(4, 'big')
				datagram += message[0:400].encode('ascii')

				print(datagram)

				client.sock.sendto(datagram, (client.ip, client.port))
				client.seqNum += 1

				client.sock.settimeout(4)

				resp = client.sock.recvfrom(406) # 2 (message type size) + 4 (sequence number size) + 400 (info or key size)

			except socket.timeout:
				print('Nenhuma resposta recebida.')


	def topoReq(client):
		try:
			datagram = (6).to_bytes(2, 'big')
			datagram += (client.seqNum).to_bytes(4, 'big')

			print(datagram)

			client.sock.sendto(datagram, (client.ip, client.port))
			client.seqNum += 1

			client.sock.settimeout(4)

			responses = []
			while not socket.timeout:
				resp = client.sock.recvfrom(406) # 2 (message type size) + 4 (sequence number size) + 400 (info or key size)

		except socket.timeout:

			try:
				datagram = (6).to_bytes(2, 'big')
				datagram += (client.seqNum).to_bytes(4, 'big')

				print(datagram)

				client.sock.sendto(datagram, (client.ip, client.port))
				client.seqNum += 1

				client.sock.settimeout(4)

				while not socket.timeout:
					responses.append(client.sock.recvfrom(406)) # 2 (message type size) + 4 (sequence number size) + 400 (info or key size)

			except socket.timeout:
				print('Nenhuma resposta recebida.')

		def checkMessageSeqNum(client, response):
			return client.seqNum == response


ipAddress, portAddress = sys.argv[1].split(':')

client = ClientInfo(ipAddress, portAddress)

print('IP:', client.ip, '\nPORT:', client.port)

while 1:
	message = input('Insira um comando:\n> ')

	if message[0].upper() == '?':
		message = message[1:].replace(' ','')
		message = message.replace('\t','')
		Message.keyReq(client, message)

	elif message[0].upper() == 'T':
		Message.topoReq(client)

	elif message[0].upper() == 'Q':
		client.sock.close()
		print('Client connection finished.')
		break

	else:
		print('Comando invalido. Por favor, insira um novo comando.\n')

	print('')