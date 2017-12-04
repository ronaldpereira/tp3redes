import sys
import socket

class ClientInfo:
	def __init__(self):
		self.serventIp, self.serventPort = sys.argv[1].split(':')
		self.serventPort = int(self.serventPort)
		self.seqNum = 0
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Option to reuse the socket address to stop giving the error: Adress is already being used when running the program multiple times

class Message:
	def sendKeyReq(client, message):
		datagram = (5).to_bytes(2, 'big')
		datagram += (client.seqNum).to_bytes(4, 'big')
		datagram += message[0:400].encode('ascii')

		print(datagram)

		client.sock.sendto(datagram, (client.serventIp, client.serventPort))
		client.seqNum += 1

		responses = []
		while 1:
			try:
				client.sock.settimeout(4)

				responses.append(client.sock.recvfrom(406)) # 2 (message type size) + 4 (sequence number size) + 400 (info or key size)

			except socket.timeout:
				if len(responses) == 0:
					datagram = (5).to_bytes(2, 'big')
					datagram += (client.seqNum).to_bytes(4, 'big')
					datagram += message[0:400].encode('ascii')

					print(datagram)

					client.sock.sendto(datagram, (client.serventIp, client.serventPort))
					client.seqNum += 1

					while 1:
						try:
							client.sock.settimeout(4)

							responses.append(client.sock.recvfrom(406)) # 2 (message type size) + 4 (sequence number size) + 400 (info or key size)

						except socket.timeout:
							if len(responses) == 0:
								print('Nenhuma resposta recebida.')
								return

							else:
								Message.printResponses((client.seqNum-1).to_bytes(4, 'big'), responses)
								return
				else:
					Message.printResponses((client.seqNum-1).to_bytes(4, 'big'), responses)
					return

	def sendTopoReq(client):
			datagram = (6).to_bytes(2, 'big')
			datagram += (client.seqNum).to_bytes(4, 'big')

			print(datagram)

			client.sock.sendto(datagram, (client.serventIp, client.serventPort))
			client.seqNum += 1

			responses = []
			while 1:
				try:
					client.sock.settimeout(4)

					responses.append(client.sock.recvfrom(406)) # 2 (message type size) + 4 (sequence number size) + 400 (info or key size)

				except socket.timeout:
					if len(responses) == 0:
						datagram = (6).to_bytes(2, 'big')
						datagram += (client.seqNum).to_bytes(4, 'big')

						print(datagram)

						client.sock.sendto(datagram, (client.serventIp, client.serventPort))
						client.seqNum += 1

						while 1:
							try:
								client.sock.settimeout(4)

								responses.append(client.sock.recvfrom(406)) # 2 (message type size) + 4 (sequence number size) + 400 (info or key size)

							except socket.timeout:
								if len(responses) == 0:
									print('Nenhuma resposta recebida.')
									return

								else:
									Message.printResponses((client.seqNum-1).to_bytes(4, 'big'), responses)
									return
					else:
						Message.printResponses((client.seqNum-1).to_bytes(4, 'big'), responses)
						return

	def printResponses(seqNum, responses):
		for response in responses:
			if response[0][2:6] == seqNum:
				print((response[0][6:]).decode(), ' ', response[1][0], ':', response[1][1], sep='')

			else:
				print('Mensagem incorreta recebida de ', response[1][0], ':', response[1][1], sep='')


client = ClientInfo()

print('SERVENT IP:', client.serventIp, '\nSERVENT PORT:', client.serventPort)

while 1:
	message = input('Insira um comando:\n> ')

	if message[0].upper() == '?':
		message = message[1:].replace(' ','').replace('\t','')
		Message.sendKeyReq(client, message)

	elif message[0].upper() == 'T':
		Message.sendTopoReq(client)

	elif message[0].upper() == 'Q':
		client.sock.close()
		print('Client connection finished.')
		break

	else:
		print('Comando invalido. Por favor, insira um novo comando.\n')

	print('')