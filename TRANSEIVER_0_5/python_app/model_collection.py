import serial
import multiprocessing
import time
class Network:
	def __init__(self):
		self.transceiver = TransceiverInterface()
		self.connections = []
		self.settings_open = False
		self.add_connections_open = False 
		self.connection = False
		
	def openSerialPort(self, serial_port_name):
		if not self.connection:
			self.transceiver.startCommunicationProcess(serial_port_name)
			self.connection = True
	
	def closeSerialPort(self):
		pass
		
	def sendPersonalMessage(self,message):
		self.transceiver.send(ord(Transciever.MESSAGING) + message)
	
	def receivePersonalMessage(self):
		return self.transceiver.receivePersonalMessage()
	
	def addConnection(self):
		pass
	
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
		while not self.state_queue.empty():
			self.state_queue.get()
		
		while not self.send_queue.empty():
			self.send_queue.get()
	
	def set_TX_address(self, address):
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
			ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout = 0.1)
			while True:                   #maybe to improve reliability put them in seperate queues
				reading = ser.readline() #brrrreeeeaaaks here
				reading = str(reading)
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
		messages = None
		if self.receive_queue != None and not self.receive_queue.empty():
			message = self.receive_queue.get()
		return message
	
	def send(self, message):
		if  ord(message[0]) == TransceiverInterface.MESSAGING:
			self.sendMediaMessage(message)
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
		self.send_queue.put(bytes(message + TransceiverInterface.FLUSH,encoding = "utf-8"))
		start = time.monotonic()
		interval = start
		success = False
		while time.monotonic() < start + 30:
			if time.monotonic() > interval + 3:
				self.send_queue.put(bytes(message + TransceiverInterface.FLUSH,encoding = "utf-8"))
				interval = time.monotonic()
				
			if not self.success_queue.empty():
				success = True
				self.success_queue.get()
				break
		
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
			print("clearing")
		
		while not self.send_queue.empty():
			self.send_queue.get()
			print("clearing")
			
		self.send_queue.put(bytes(chr(TransceiverInterface.SET_TX_ADDRESS) + self.tx_address + TransceiverInterface.FLUSH, encoding = "utf-8"))
		#cycle through address that return a success and there is our list
		
			
		return addresses
				
	
	def __del__(self):
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
	


		
		
			
		