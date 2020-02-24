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
		#connections = self.transceiver.finding()
		return ["debug"] * 20

class TransceiverInterface:
	MESSAGING = 0
	SET_TX_ADDRESS = 1
	SET_RX_ADDRESS = 2
	GET_TX_ADDRESS = 3
	GET_RX_ADDRESS = 4
	TOGGLE_SUCCESS_MODE = 5
	GET_SUCCESS_MODE = 6
	TOGGLE_LED = 7
	FLUSH = '\r'   #should use something different
	
	def __init__(self, SERIAL_PORT_NAME = None, BAUD_RATE = 9600): # there might need to be a node ID nodeid = A, and tx = 00000 and rx = 11111
		self.communicationProcess = None
		self.send_queue = None
		self.receive_queue = None
		self.state_queue = None
		self.address_queue = None
		self.file_queue = None
		self.success_queue = None
		self.id = None
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
	
	def stopCommunicationProcess(self):
		pass

	@staticmethod
	def communication(obj, SERIAL_PORT_NAME, BAUD_RATE,send_queue, receive_queue, state_queue, address_queue, success_queue):         #gets the receiving messages in a parallel process # this gets put under cases
		ser = None
		try:
			ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout = 0.2)
			while True:                   #maybe to improve reliability put them in seperate queues
				reading = ser.readline() #brrrreeeeaaaks here
				reading = str(reading)
				original = reading
				reading = reading[2:len(reading) - 1]
			
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
					ser.write(send_queue.get())
					
				if "b''" == original:
					continue
				print("\r" + reading + (" " * 50) + "\n")
				print("\nEnter a message to write:",end="")
		except:
			pass
		finally:
			ser.close()
			
	def formatReceivedMessage(self, message):
		copy_of_message = message
		try:                                          #if you remove the try except and type clear, the INVALID state message will cause reading.index(':') to throw an exception
			l = message.index(':') + 1
			if "\\x" in message:
				message = message[l:len(message) - 2]
			else:
				r = message.index('\\')
				message = message[l:r + 1]
		except Exception as e:
			print(e)
			message = copy_of_message
		return message
			
	def receivePersonalMessage(self):
		messages = None
		if self.receive_queue != None and not self.receive_queue.empty():
			message = self.receive_queue.get()
		return message
	
	def send(self, message):
		if ord(message[0]) == TransceiverInterface.MESSAGING:
			self.sendMediaMessage(message)
		else:
			self.send_queue.put(bytes(message + TransceiverInterface.FLUSH,encoding = "utf-8"))
			
		
	def sendMediaMessage(self, message): #this has a protocol to retransmit if fails through, yap I know its not using autoack
		self.send_queue.put(bytes(message + Transeiver.FLUSH,encoding = "utf-8"))
		start = time.monotonic()
		success = False
		while time.monotonic() < start + 30:
			if self.success_queue.empty() and time.monotonic() > start + 3:
				self.send_queue.put(bytes(message + Transceiver.FLUSH,encoding = "utf-8"))
			else:
				success = True
				self.success_queue.get()
				break
		
		if success:
			print("message sent!")
		else:
			print("message fail")
		return success
				
		
	
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
	


		
		
			
		