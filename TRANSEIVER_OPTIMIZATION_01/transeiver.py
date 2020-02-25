import serial
import multiprocessing
import time

class Transeiver:
	MESSAGING = '0'
	SET_TX_ADDRESS = '1'
	SET_RX_ADDRESS = '2'
	GET_TX_ADDRESS = '3'
	GET_RX_ADDRESS = '4'
	TOGGLE_SUCCESS_MODE = '5'
	GET_SUCCESS_MODE = '6'
	TOGGLE_LED = '7'
	FLUSH = '\r'   #should use something different
	
	def __init__(self, TXaddress = "?????", RXaddress = "!!!!!", SERIAL_PORT_NAME = None, BAUD_RATE = 9600): # there might need to be a node ID nodeid = A, and tx = 00000 and rx = 11111
		self.serial_port = None
		self.TXaddress = TXaddress
		self.RXaddress = RXaddress
		self.fetchMessagesProcess = None
		self.receive_queue = None
		self.state_queue = None
		self.address_queue = None
		self.success_mode = False
		if SERIAL_PORT_NAME != None:
			self.setConnection(SERIAL_PORT_NAME, BAUD_RATE)
	
	def setConnection(self, SERIAL_PORT_NAME, BAUD_RATE):
		self.serial_port = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE)
		self.jottleConnection()
		self.startParallelReceivingProcess()
		self.setTXaddress(self.TXaddress)
		self.setRXaddress(self.RXaddress)
		self.serial_port.flush()

	def jottleConnection(self):
		time.sleep(0.1)
		self.serial_port.setDTR(False) #this prevents a lock up how does it work?
		time.sleep(0.1)
		self.serial_port.setRTS(True) #this prevents a lock up how does it work?
		time.sleep(0.1)
	
	def startParallelReceivingProcess(self):
		self.receive_queue = multiprocessing.Queue()
		self.state_queue = multiprocessing.Queue()
		self.address_queue = multiprocessing.Queue()
		self.fetchMessagesProcess = multiprocessing.Process(target = Transeiver.receiving, args = (self,self.serial_port, self.receive_queue, self.state_queue, self.address_queue)) #maybe just make a new one
		self.fetchMessagesProcess.start()
		
		
	def setAddresses(self, TXaddress, RXaddress):
		self.setTXaddress(TXaddress)
		self.setRXaddress(RXaddress)
	
	def setTXaddress(self, TXaddress):
		self.serial_port.write(bytes(Transeiver.SET_TX_ADDRESS + TXaddress + Transeiver.FLUSH,encoding = 'utf-8')) #redundant but I think it clarifies the code
		self.serial_port.write(bytes(Transeiver.GET_TX_ADDRESS + Transeiver.FLUSH, encoding = 'utf-8'))
		self.TXaddress = self.state_queue.get()
	
	def setRXaddress(self, RXaddress):
		self.serial_port.write(bytes(Transeiver.SET_RX_ADDRESS + RXaddress + Transeiver.FLUSH,encoding = 'utf-8'))
		self.serial_port.write(bytes(Transeiver.GET_RX_ADDRESS + Transeiver.FLUSH, encoding = 'utf-8'))
		self.RXaddress = self.state_queue.get()
	
	def getTXaddress(self):
		return self.TXaddress
	
	def getRXaddress(self):
		return self.RXaddress
	
	def isSuccessMode(self):
		return self.success_mode
		
	def toggleSuccessMode(self):
		self.serial_port.flush()
		self.serial_port.write(bytes(Transeiver.TOGGLE_SUCCESS_MODE + Transeiver.FLUSH, encoding = 'utf-8'))
		self.serial_port.write(bytes(Transeiver.GET_SUCCESS_MODE + Transeiver.FLUSH, encoding = 'utf-8'))
		value = self.state_queue.get()
		if value.isnumeric():
			self.success_mode = bool(int(value))
		else:
			self.success_mode = False
		
		
	def printSerialPortState(self):
		print("DTR: ", self.serial_port.dtr)
		print("RTS: ", self.serial_port.rts)
		print("CTS: ", self.serial_port.cts)
		print("DSR: ", self.serial_port.dsr)
		print("RI: ", self.serial_port.ri)
		print("CD: ", self.serial_port.cd)

	@staticmethod
	def receiving(obj, ser,receive_queue, state_queue, address_queue):         #gets the receiving messages in a parallel process # this gets put under cases
		cant_decode = False
		while True:                   #maybe to improve reliability put them in seperate queues
			reading = ser.readline() #brrrreeeeaaaks here
			reading = str(reading)
			reading = reading[2:len(reading) - 1]
			if "ADDRESS-" in reading:
				reading = obj.formatReceivedMessage(reading)    #should use obj instead since self makes it misleading
				address_queue.put(reading)
			elif "STATE:" in reading:
				reading = obj.formatReceivedMessage(reading)
				state_queue.put(reading)
			elif "RECEIVED:" in reading or "SUCCESS:" in reading:
				reading = obj.formatReceivedMessage(reading)
				receive_queue.put(reading)
			print("\r" + str(reading) + (" " * 50) + "\n")
			print("\nEnter a message to write:",end="")
			
	def formatReceivedMessage(self, message):
		copy_of_message = message
		try:                                          #if you remove the try except and type clear, the INVALID state message will cause reading.index(':') to throw an exception
			l = message.index(':') + 1
			if "\\x" in message:
				message = message[l:len(message) - 3]
			else:
				r = message.index('\\')
				message = message[l:r]
		except Exception as e:
			print(e)
			message = copy_of_message
		return message
			
	def getMessage(self):
		messages = None
		if self.receive_queue != None and not self.receive_queue.empty():
			message = self.receive_queue.get()
		return message
	
	
	def sendMessage(self, message):
		if message == "":
			return
		elif message[0] == Transeiver.MESSAGING:
			self.serial_port.write(bytes(message + Transeiver.FLUSH, encoding = 'utf-8'))
		elif message[0] == Transeiver.SET_TX_ADDRESS:
			self.setTXaddress(message[1:])
		elif message[0] == Transeiver.SET_RX_ADDRESS:
			self.setRXaddress(message[1:])
		elif message[0] == Transeiver.GET_TX_ADDRESS:
			#self.receive_queue.put(self.TXaddress)  <----- this will be used when added to GUI
			print(self.TXaddress) #yeah the point of this was not to have to put the addresses back into queue
		elif message[0] == Transeiver.GET_RX_ADDRESS:
			#self.receive_queue.put(self.RXaddress)  <------ this will be used when added to gui
			print(self.RXaddress)
		elif message[0] == Transeiver.TOGGLE_SUCCESS_MODE:   #this toggles the success protocol
			self.toggleSuccessMode()
		elif message[0] == Transeiver.GET_SUCCESS_MODE:   #this toggles the success protocol
			#self.receive_queue.put(self.success_mode)
			print("send message success mode:",self.success_mode)
		elif message[0] == Transeiver.TOGGLE_LED:
			self.serial_port.write(bytes(Transeiver.TOGGLE_LED + Transeiver.FLUSH, encoding = 'utf-8'))
			
	
	def __del__(self):
		self.fetchMessagesProcess.terminate()
		self.serial_port.close()


class MasterTranseiver(Transeiver):    #some networks have properties, some with changing address or those that are not available #central ID for node might be needed
	SEARCHING_ADDRESS_A = "!!!!!"   #must state that these are reserved addresses #what kind of goal does this satisfy
	SEARCHING_ADDRESS_B = "?????"    #can be in a constant searching mode
	DISCOVERY = '8'
	FINDING = '9'
	ADDRESS_MESSAGE_SIZE = 13       #example. ADDRESS-12345  which is 13 characters
	def __init__(self,TXaddress = "?????", RXaddress = "!!!!!", SERIAL_PORT_NAME = None, BAUD_RATE = 9600):
		super().__init__(TXaddress, RXaddress, SERIAL_PORT_NAME, BAUD_RATE)
		self.neighboring_nodes = []

	
	def finding(self):
		if self.success_mode:
			self.toggleSuccessMode()
		ADDRESS_A = MasterTranseiver.SEARCHING_ADDRESS_A
		ADDRESS_B = MasterTranseiver.SEARCHING_ADDRESS_B
		self.serial_port.write(bytes(Transeiver.SET_TX_ADDRESS + ADDRESS_A + Transeiver.FLUSH, encoding = 'utf-8'))
		time.sleep(0.2)
		self.serial_port.write(bytes(Transeiver.SET_RX_ADDRESS + ADDRESS_B + Transeiver.FLUSH, encoding = 'utf-8'))
		time.sleep(0.2)
		end_time = time.monotonic() + 60
		message = None
		while time.monotonic() < end_time:
			self.serial_port.write(bytes(Transeiver.MESSAGING + "ADDRESS-" + self.RXaddress + Transeiver.FLUSH,encoding = 'utf-8'))
			time.sleep(0.2)
			print("sent")
			if not self.address_queue.empty():
				message = self.address_queue.get()
				print("received")
				if self.validAddress(message):
					print("added")
					self.neighboring_nodes.append(message)
		time.sleep(0.2)
		self.serial_port.write(bytes(Transeiver.SET_TX_ADDRESS + self.TXaddress + Transeiver.FLUSH, encoding = 'utf-8'))
		time.sleep(0.2)
		self.serial_port.write(bytes(Transeiver.SET_RX_ADDRESS + self.RXaddress + Transeiver.FLUSH, encoding = 'utf-8'))
					
		print(self.neighboring_nodes)
		self.toggleSuccessMode()

	def discovery(self):
		if self.success_mode:
			self.toggleSuccessMode()
		ADDRESS_A = MasterTranseiver.SEARCHING_ADDRESS_A
		ADDRESS_B = MasterTranseiver.SEARCHING_ADDRESS_B
		self.serial_port.write(bytes(Transeiver.SET_TX_ADDRESS + ADDRESS_B + Transeiver.FLUSH, encoding = 'utf-8'))
		time.sleep(0.2)
		self.serial_port.write(bytes(Transeiver.SET_RX_ADDRESS + ADDRESS_A + Transeiver.FLUSH, encoding = 'utf-8'))
		time.sleep(0.2)
		end_time = time.monotonic() + 60
		message = None
		while time.monotonic() < end_time:
			if not self.address_queue.empty():
				message = self.address_queue.get()
				print("received")
				self.serial_port.write(bytes(Transeiver.MESSAGING + "ADDRESS-" + self.RXaddress + Transeiver.FLUSH,encoding = 'utf-8'))
				if self.validAddress(message): 
					print("added")
					self.neighboring_nodes.append(message)
		time.sleep(0.2)
		self.serial_port.write(bytes(Transeiver.SET_TX_ADDRESS + self.TXaddress + Transeiver.FLUSH, encoding = 'utf-8'))
		time.sleep(0.2)
		self.serial_port.write(bytes(Transeiver.SET_RX_ADDRESS + self.RXaddress + Transeiver.FLUSH, encoding = 'utf-8'))
				
		print(self.neighboring_nodes)
		self.toggleSuccessMode()

	def validAddress(self, message):
		return message not in self.neighboring_nodes and "ADDRESS-" in message and len(message) == MasterTranseiver.ADDRESS_MESSAGE_SIZE
	

	def sendMessage(self, message):  #can use object oriented programming to access the super classes send
		if message == "":
			return
		elif message[0] == MasterTranseiver.DISCOVERY:
			self.discovery()
		elif message[0] == MasterTranseiver.FINDING:
			self.finding()
		else:
			super().sendMessage(message)
	
	def clean_neighboring_node_list(self):
		pass
		
		
		
			
		