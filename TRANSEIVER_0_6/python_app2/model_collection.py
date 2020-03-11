import serial
import multiprocessing
import time
import util 

class Network:
	def __init__(self):
		self.transceiver = TransceiverInterface()
		self.connections = dict()
		self.settings_open = False
		self.add_connections_open = False 
		self.connection = False
		self.message_number = 1
		self.message_complete = False
		self.send_buffer = []
		self.receive_buffer = ""
		self.sent_last_line = False
		self.sent_first_line = True
		self.chunk_length = 28
		self.message_last_sent = "";
		self.message_controller_created = False
		
	def openSerialPort(self, serial_port_name):
		if not self.connection:
			self.transceiver.startCommunicationProcess(serial_port_name)
			self.connection = True
	
	def closeSerialPort(self):
		pass
	
	def isMessageControllerCreated(self):
		return self.message_controller_created
	
	def setMessageControllerCreated(self, value):
		self.message_controller_created = value
	
	def clearBuffer(self):
		self.send_buffer = []
	
	def incrementMessageNumber(self):
		self.message_number += 1
	
	def setSendingAddress(self, address):
		print("setting sending address")
		self.transceiver.set_TX_address(address)
	
	def getMessageNumber(self):
		return self.message_number
		
	def loadAddress(self, addresses):
		self.addresses = addresses
		self.setSendingAddress(self.addresses.pop(0))
		
	def load(self, message):
		self.send_buffer = util.messageChunks(message, self.chunk_length)
		self.send_buffer.append(chr(0)) #marks end of buffer
	
	def getMessageLastSent(self):
		return self.message_last_sent
	
	def getFailedMessage(self):
		message = self.message_last_sent
		self.message_last_sent = ""
		return message
	
	def setMessageLastSent(self,value):
		self.message_last_sent = value
		
	"""	
	def send(self):
		self.message_last_sent = str(self.message_number)
		while not self.empty():
			message = self.send_buffer.pop(0)
			if message != chr(0):
				self.message_last_sent +=  "\t" + message + "\n"
			if not self.transceiver.sendMediaMessage(message):
				return False
		self.message_number += 1
		return True
	"""
	
	def send(self):
		if self.message_last_sent == "":
			self.message_last_sent = str(self.message_number)
			
		if not self.empty():
			message = self.send_buffer.pop(0)
			if message != chr(0):
				self.message_last_sent +=  "\t" + message + "\n"
			else:
				self.message_number += 1
				#if len(self.addresses) > 0:
				#	self.setSendingAddress(self.addresses.pop(0))
					
			if not self.transceiver.sendMediaMessage(message):
				self.message_number += 1
				return False
		else:
			self.message_last_sent = ""
			
		
		return True
	
	
	def sentFirstLine(self):
		return self.sent_first_line
	
	def sentLastLine(self):
		return self.sent_last_line
	
	def setSentFirstLine(self, value):
		self.sent_first_line = value
	
	def setSentLastLine(self,value):
		self.sent_last_line = value
	
	def empty(self):
		return len(self.send_buffer) == 0
	
	def isMessageComplete(self):
		return self.message_complete
	
	def setMessageComplete(self, value):
		self.message_complete = value
	
	def receivePersonalMessage(self):
		return self.transceiver.receivePersonalMessage()
	
	def receive(self):
		message = self.transceiver.receivePersonalMessage()
		
		if message != None  and "\\x" not in message and message != "" and message != "\n":
			if self.receive_buffer == "":
				self.receive_buffer += str(self.message_number) +"\t" + message + "\n"
			else:
				self.receive_buffer += " \t" + message + "\n"
			return None
		
		if message == "":
			receive = self.receive_buffer
			self.receive_buffer = ""
			self.message_number += 1
			return receive
			
		return None
		
	
	def addConnection(self, connection):
		self.connections[connection.getViewName()] = connection
	
	def removeConnection(self, connection_name):
		if connection_name in self.connections:
			del self.connections[connection_name]
	
	def resetMessageNumber(self):
		self.message_number = 1
	
	def isSettingsOpen(self):
		return self.settings_open
	
	def setSettingsOpen(self, value):
		self.settings_open = value
	
	def isAddConnectionsOpen(self):
		return self.add_connections_open
	
	def setAddConnectionsOpen(self,value):
		self.add_connections_open = value
	
	def findConnections(self):
		connections = self.transceiver.finding()
		return connections

class TransceiverInterface:
	MESSAGING = 0
	SET_TX_ADDRESS = 1
	SET_RX_ADDRESS = 2
	GET_TX_ADDRESS = 3
	GET_RX_ADDRESS = 4
	TOGGLE_SUCCESS_MODE = 5
	GET_SUCCESS_MODE = 6
	TOGGLE_LED = 7
	FINDING = 8
	FINDING_ADDRESS = "\x00!!"
	ADDRESS_RETURN = "2"
	FLUSH = '\r'   #should use something different
	
	def __init__(self, SERIAL_PORT_NAME = None, BAUD_RATE = 9600): # there might need to be a node ID nodeid = A, and tx = 00000 and rx = 11111
		self.communicationProcess = None
		self.send_queue = None
		self.receive_queue = None
		self.state_queue = None
		self.address_queue = None
		self.file_queue = None
		self.success_queue = None
		self.rx_address = [0,0,0,0,0,0]
		self.tx_address = None
		if SERIAL_PORT_NAME != None:
			self.startCommunicationProcess(SERIAL_PORT_NAME, BAUD_RATE)

	
	def startCommunicationProcess(self, SERIAL_PORT_NAME, BAUD_RATE = 9600):
		self.receive_queue = multiprocessing.Queue()
		self.send_queue = multiprocessing.Queue()
		self.state_queue = multiprocessing.Queue()
		self.address_queue = multiprocessing.Queue()
		self.success_queue = multiprocessing.Queue()
		self.communicationProcess = multiprocessing.Process(target = TransceiverInterface.communication, args = (self,SERIAL_PORT_NAME, BAUD_RATE, self.send_queue, self.receive_queue, self.state_queue, self.address_queue, self.success_queue)) #maybe just make a new one
		self.communicationProcess.start()
		self.get_TX_address_from_node()
		self.get_RX_address_from_node(chr(0))
		self.get_RX_address_from_node(chr(1))
		self.get_RX_address_from_node(chr(2))
		self.get_RX_address_from_node(chr(3))
		self.get_RX_address_from_node(chr(4))
		self.get_RX_address_from_node(chr(5))
		
	
	def stopCommunicationProcess(self):
		pass
		
	def get_TX_address(self):
		return self.tx_address
	
	def get_TX_address_from_node(self):
		self.send_queue.put(bytes(chr(TransceiverInterface.GET_TX_ADDRESS) + TransceiverInterface.FLUSH, encoding = "utf-8"))
		start = time.monotonic()
		while self.state_queue.empty():
			if time.monotonic() > start + 0.25:
				self.send_queue.put(bytes(chr(TransceiverInterface.GET_TX_ADDRESS) + TransceiverInterface.FLUSH, encoding = "utf-8"))
				start = time.monotonic()
		self.tx_address = self.state_queue.get()
		print("setting address success: ", self.tx_address)
		while not self.state_queue.empty():
			self.state_queue.get()
		
		while not self.send_queue.empty():
			self.send_queue.get()
	
	def set_TX_address(self, address):
		print("setting address: ", address)
		self.send_queue.put(bytes(chr(TransceiverInterface.SET_TX_ADDRESS) + address + TransceiverInterface.FLUSH, encoding = "utf-8"))
		self.get_TX_address_from_node()
		
	
	def get_RX_address(self, pipe):
		return self.rx_address[pipe]
	
	def get_RX_address_from_node(self, pipe):
		self.send_queue.put(bytes(chr(TransceiverInterface.GET_RX_ADDRESS) + pipe + TransceiverInterface.FLUSH, encoding = "utf-8"))
		start = time.monotonic()
		while self.state_queue.empty() :
			if time.monotonic() > start + 0.25:
				self.send_queue.put(bytes(chr(TransceiverInterface.GET_RX_ADDRESS) + pipe + TransceiverInterface.FLUSH, encoding = "utf-8"))
				start = time.monotonic()
		self.rx_address[ord(pipe)] = self.state_queue.get()
		while not self.state_queue.empty():
			self.state_queue.get()
		
		while not self.send_queue.empty():
			self.send_queue.get()
			
	
	def set_RX_address(self, address,pipe):
		self.send_queue.put(bytes(chr(TransceiverInterface.SET_RX_ADDRESS) + pipe + address + TransceiverInterface.FLUSH, encoding = "utf-8"))
		self.get_RX_address_from_node(pipe)

	@staticmethod
	def communication(obj, SERIAL_PORT_NAME, BAUD_RATE,send_queue, receive_queue, state_queue, address_queue, success_queue):         #gets the receiving messages in a parallel process # this gets put under cases
		ser = None
		try:
			ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout = 0.10)
			while True:                   #maybe to improve reliability put them in seperate queues
				reading = ser.readline() #brrrreeeeaaaks here
				reading = str(reading)
				if reading != "b''":
					print("com:" + reading)
				original = reading
				if "ADDRESS:" in reading:
					reading = obj.formatReceivedMessage(reading)    #should use obj instead since self makes it misleading
					address_queue.put(reading)
				elif "STATE:" in reading:
					reading = obj.formatReceivedMessage(reading)
					state_queue.put(reading)
				elif "RECEIVED:" in reading:
					reading = obj.formatReceivedMessage(reading)
					receive_queue.put(reading)
				elif "SUCCESS:" in reading:
					reading = obj.formatReceivedMessage(reading)
					success_queue.put(reading)
					continue
				
				if(not send_queue.empty()):
					hmm = send_queue.get()
					print(hmm)
					ser.write(hmm)
					
				if "b''" == original:
					continue
				print("\r" + reading + (" " * 50) + "\n")
				print("\nEnter a message to write:",end="")
		except Exception as e:
			print(e)
		finally:
			ser.close()
			
	def formatReceivedMessage(self, message):
		copy_of_message = message
		try:                                          #if you remove the try except and type clear, the INVALID state message will cause reading.index(':') to throw an exception
			l = message.index(':') + 1
			r = message.rindex('\\')
			message = message[l : r]
		except Exception as e:
			print("cant format: " , e)
			message = copy_of_message
		return message
			
	def receivePersonalMessage(self):
		message = None
		if self.receive_queue != None and not self.receive_queue.empty():
			message = self.receive_queue.get()
		return message
	
	def send(self, message):
		if  ord(message[0]) == TransceiverInterface.MESSAGING:
			self.sendMediaMessage(message[1:])
		elif ord(message[0]) == TransceiverInterface.SET_TX_ADDRESS:
			self.set_TX_address(message[1:4])
		elif ord(message[0]) == TransceiverInterface.SET_RX_ADDRESS:
			self.set_RX_address(message[2:5], chr(ord(message[1]) - ord("0")))
		elif ord(message[0]) == TransceiverInterface.GET_TX_ADDRESS:
			self.get_TX_address_from_node()
		elif ord(message[0]) == TransceiverInterface.GET_RX_ADDRESS:
			self.get_RX_address_from_node(chr(ord(message[1]) - ord("0")))
		elif ord(message[0]) == TransceiverInterface.FINDING:
			self.finding()
		else:
			self.send_queue.put(bytes(message + TransceiverInterface.FLUSH,encoding = "utf-8"))
			
		
	def sendMediaMessage(self, message): #this has a protocol to retransmit if fails through, yap I know its not using autoack
		print(message)
		self.send_queue.put(bytes(chr(TransceiverInterface.MESSAGING) + message + TransceiverInterface.FLUSH,encoding = "utf-8"))
		start = time.monotonic()
		interval = start
		success = False
		
		while not self.success_queue.empty(): # this success queue might need to be fixed longer
			self.success_queue.get()
			
		while time.monotonic() < start + 15:
			if time.monotonic() > interval + 1:
				print("sent again")
				self.send_queue.put(bytes(chr(TransceiverInterface.MESSAGING) + message + TransceiverInterface.FLUSH,encoding = "utf-8"))
				interval = time.monotonic()
				
			if not self.success_queue.empty():
				success = True
				self.success_queue.get()   #sometimes wrong here
				break   
				
		while not self.send_queue.empty():
			self.send_queue.get()
			#print("clearing")
		
		while not self.success_queue.empty(): # this success queue might need to be fixed longer
			self.success_queue.get()
			#print("clearing")
		
		if success:
			print("message sent!")
		else:
			print("message fail")
		return success
		
	
	def finding(self):
		self.send_queue.put(bytes(chr(TransceiverInterface.SET_TX_ADDRESS) + TransceiverInterface.FINDING_ADDRESS + TransceiverInterface.FLUSH, encoding = "utf-8"))
		start = time.monotonic()
		interval = start
		addresses = []
		self.send_queue.put(bytes(chr(TransceiverInterface.MESSAGING) + TransceiverInterface.ADDRESS_RETURN + self.rx_address[0] + TransceiverInterface.FLUSH, encoding = "utf-8"))
		while time.monotonic() < start + 15:
			if time.monotonic() > interval + 0.10:
				print("searching")
				self.send_queue.put(bytes(chr(TransceiverInterface.MESSAGING) + TransceiverInterface.ADDRESS_RETURN + self.rx_address[0] + TransceiverInterface.FLUSH, encoding = "utf-8"))
				interval = time.monotonic()
			if not self.address_queue.empty():
				print("received")
				address = self.address_queue.get()
				print(address)
				if address not in addresses:
					addresses.append(address)
		
		for address in addresses:
			print("found address:",address)
			
		while not self.address_queue.empty():
			self.address_queue.get()
			#print("clearing")
		
		while not self.send_queue.empty():
			self.send_queue.get()
			#print("clearing")
		
		
		self.send_queue.put(bytes(chr(TransceiverInterface.SET_TX_ADDRESS) + self.tx_address + TransceiverInterface.FLUSH, encoding = "utf-8"))
		#cycle through address that return a success and there is our list
		
			
		return addresses
				
	
	def __del__(self):
		self.communicationProcess.join()
		self.communicationProcess.terminate()
		self.receive_queue.close()
		self.send_queue.close()
		self.state_queue.close()
		self.address_queue.close()
		self.file_queue.close()
		self.success_queue.close()



class MasterTransceiverInterface(TransceiverInterface):
	def __init__(self):
		pass
	


		
		
			
		