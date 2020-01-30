import serial
import multiprocessing
import time


class Transeiver:
	MESSAGING = '0'
	SET_TX_ADDRESS = '1'
	SET_RX_ADDRESS = '2'
	GET_TX_ADDRESS = '3'
	GET_RX_ADDRESS = '4'
	FLUSH = '\r'   #should use something different
	
	def __init__(self, TXaddress = "?????", RXaddress = "!!!!!", SERIAL_PORT_NAME = None, BAUD_RATE = 9600): # there might need to be a node ID nodeid = A, and tx = 00000 and rx = 11111
		self.serial_port = None
		self.TXaddress = TXaddress
		self.RXaddress = RXaddress
		self.__fetchMessagesProcess = None
		self.receive_queue = None
		if SERIAL_PORT_NAME != None:
			self.setConnection(SERIAL_PORT_NAME, BAUD_RATE)
	
	def setConnection(self, SERIAL_PORT_NAME, BAUD_RATE):
		self.serial_port = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE)
		self.__jottleConnection()
		self.__startParallelReceivingProcess()
		self.setTXaddress(self.TXaddress)
		self.setRXaddress(self.RXaddress)

	def __jottleConnection(self):
		time.sleep(0.1)
		self.serial_port.setDTR(False) #this prevents a lock up how does it work?
		time.sleep(0.1)
		self.serial_port.setRTS(True) #this prevents a lock up how does it work?
		time.sleep(0.1)
	
	def __startParallelReceivingProcess(self):
		self.receive_queue = multiprocessing.Queue()
		self.__fetchMessagesProcess = multiprocessing.Process(target = Transeiver.receiving, args = (self.serial_port, self.receive_queue)) #maybe just make a new one
		self.__fetchMessagesProcess.start()
		
		
	def setAddresses(self, TXaddress, RXaddress):
		self.setTXaddress(TXaddress)
		self.setRXaddress(RXaddress)
	
	def setTXaddress(self, TXaddress):
		self.serial_port.write(bytes(Transeiver.SET_TX_ADDRESS + self.TXaddress + Transeiver.FLUSH,encoding = 'utf-8')) #redundant but I think it clarifies the code
		self.serial_port.write(bytes(Transeiver.GET_TX_ADDRESS + Transeiver.FLUSH, encoding = 'utf-8'))
		self.TXaddress = self.receive_queue.get()
	
	def setRXaddress(self, RXaddress):
		self.serial_port.write(bytes(Transeiver.SET_RX_ADDRESS + self.RXaddress + Transeiver.FLUSH,encoding = 'utf-8'))
		self.serial_port.write(bytes(Transeiver.GET_RX_ADDRESS + Transeiver.FLUSH, encoding = 'utf-8'))
		self.RXaddress = self.receive_queue.get()
	
	def getTXaddress(self):
		return self.TXaddress
	
	def getRXaddress(self):
		return self.RXaddress
	
	def printSerialPortState(self):
		print("DTR: ", self.serial_port.dtr)
		print("RTS: ", self.serial_port.rts)
		print("CTS: ", self.serial_port.cts)
		print("DSR: ", self.serial_port.dsr)
		print("RI: ", self.serial_port.ri)
		print("CD: ", self.serial_port.cd)
		
	@staticmethod
	def receiving(ser,queue):         #gets the receiving messages in a parallel process
		cant_decode = False
		while True:
			reading = ser.readline()
			reading = str(reading)
			try:                                          #if you remove the try except and type clear, the INVALID state message will cause reading.index(':') to throw an exception
				l = reading.index(':') + 1
				if "\\x" in reading:
					reading = reading[l:len(reading) - 3]
				else:
					r = reading.index('\\')
					reading = reading[l:r]
			except:
				pass
			queue.put(reading)
			print("\r" + str(reading) + (" " * 50) + "\n")
			print("\nEnter a message to write:",end="")

	def getMessage(self):
		messages = None
		if self.receive_queue != None and not self.receive_queue.empty():
			message = self.receive_queue.get()
		return message
	
	
	def sendMessage(self, message):
		self.serial_port.write(bytes(message + Transeiver.FLUSH, encoding = 'utf-8'))
	
	def __del__(self):
		self.__fetchMessagesProcess.terminate()
		self.serial_port.close()


class MasterTranseiver(Transeiver):    #some networks have properties, some with changing address or those that are not available #central ID for node might be needed
	SEARCHING_ADDRESS_A = "!!!!!"   #must state that these are reserved addresses #what kind of goal does this satisfy
	SEARCHING_ADDRESS_B = "?????"    #can be in a constant searching mode
	DISCOVERY = '5'
	FINDING = '6'
	def __init__(self,TXaddress = "?????", RXaddress = "!!!!!", SERIAL_PORT_NAME = None, BAUD_RATE = 9600):
		super().__init__(TXaddress, RXaddress, SERIAL_PORT_NAME, BAUD_RATE)
		self.neighboring_nodes = []
	
	def __search(self, mode = 0):
		ADDRESS_A = MasterTranseiver.SEARCHING_ADDRESS_A
		ADDRESS_B = MasterTranseiver.SEARCHING_ADDRESS_B
		if mode != 1:
			temp = ADDRESS_A
			ADDRESS_A = ADDRESS_B
			ADDRESS_B = ADDRESS_A
		self.serial_port.write(bytes(Transeiver.SET_TX_ADDRESS + ADDRESS_A + Transeiver.FLUSH, encoding = 'utf-8'))
		self.serial_port.write(bytes(Transeiver.SET_RX_ADDRESS + ADDRESS_B + Transeiver.FLUSH, encoding = 'utf-8'))
		end_time = time.monotonic() + 30
		message = None
		while time.monotonic() < end_time:
			self.serial_port.write(bytes(Transeiver.MESSAGING + self.TXaddress + Transeiver.FLUSH,encoding = 'utf-8'))
			if not self.receive_queue.empty():
				message = self.receive_queue.get()
				if message != '' and message != "<<<success>>>" and message not in self.neighboring_nodes: #the code should stop using this success protocol
					self.neighboring_nodes.append(message)
		self.serial_port.write(bytes(Transeiver.SET_TX_ADDRESS + self.TXaddress + Transeiver.FLUSH, encoding = 'utf-8'))
		self.serial_port.write(bytes(Transeiver.SET_RX_ADDRESS + self.RXaddress + Transeiver.FLUSH, encoding = 'utf-8'))
					
		print(self.neighboring_nodes)

	def sendMessage(self, message):
		if message[0] != MasterTranseiver.DISCOVERY and message[0] != MasterTranseiver.FINDING:
			self.serial_port.write(bytes(message + Transeiver.FLUSH, encoding = 'utf-8'))
		elif message[0] == MasterTranseiver.DISCOVERY:
			self.__search(0)
		elif message[0] == MasterTranseiver.FINDING:
			self.__search(1)
	
	def clean_neighboring_node_list(self):
		pass
		
		
		
			
		