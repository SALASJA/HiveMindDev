import serial
import multiprocessing
import time


class Transeiver:
	__MESSAGING = '0'
	__SET_TX_ADDRESS = '1'
	__SET_RX_ADDRESS = '2'
	__GET_TX_ADDRESS = '3'
	__GET_RX_ADDRESS = '4'
	__FLUSH = '\r'   #should use something different
	
	def __init__(self, TXaddress = "00000", RXaddress = "11111", SERIAL_PORT_NAME = None, BAUD_RATE = 9600):
		self.__serial_port = None
		self.TXaddress = TXaddress
		self.RXaddress = RXaddress
		self.__fetchMessagesProcess = None
		self.__receive_queue = None
		if SERIAL_PORT_NAME != None:
			self.setConnection(SERIAL_PORT_NAME, BAUD_RATE)
	
	def setConnection(self, SERIAL_PORT_NAME, BAUD_RATE):
		self.__serial_port = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE)
		self.__jottleConnection()
		self.__startParallelReceivingProcess()
		self.setTXaddress(self.TXaddress)
		self.setRXaddress(self.RXaddress)

	def __jottleConnection(self):
		time.sleep(0.1)
		self.__serial_port.setDTR(False) #this prevents a lock up how does it work?
		time.sleep(0.1)
		self.__serial_port.setRTS(True) #this prevents a lock up how does it work?
		time.sleep(0.1)
	
	def __startParallelReceivingProcess(self):
		self.__receive_queue = multiprocessing.Queue()
		self.__fetchMessagesProcess = multiprocessing.Process(target = Transeiver.receiving, args = (self.__serial_port, self.__receive_queue)) #maybe just make a new one
		self.__fetchMessagesProcess.start()
		
		
	def setAddresses(self, TXaddress, RXaddress):
		self.setTXaddress(TXaddress)
		self.setRXaddress(RXaddress)
	
	def setTXaddress(self, TXaddress):
		self.__serial_port.write(bytes(Transeiver.__SET_TX_ADDRESS + self.TXaddress + Transeiver.__FLUSH,encoding = 'utf-8')) #redundant but I think it clarifies the code
		self.__serial_port.write(bytes(Transeiver.__GET_TX_ADDRESS + Transeiver.__FLUSH, encoding = 'utf-8'))
		self.TXaddress = self.__receive_queue.get()
	
	def setRXaddress(self, RXaddress):
		self.__serial_port.write(bytes(Transeiver.__SET_RX_ADDRESS + self.RXaddress + Transeiver.__FLUSH,encoding = 'utf-8'))
		self.__serial_port.write(bytes(Transeiver.__GET_RX_ADDRESS + Transeiver.__FLUSH, encoding = 'utf-8'))
		self.RXaddress = self.__receive_queue.get()
	
	def getTXaddress(self):
		return self.TXaddress
	
	def getRXaddress(self):
		return self.RXaddress
	
	def __printSerialPortState(self):
		print("DTR: ", self.__serial_port.dtr)
		print("RTS: ", self.__serial_port.rts)
		print("CTS: ", self.__serial_port.cts)
		print("DSR: ", self.__serial_port.dsr)
		print("RI: ", self.__serial_port.ri)
		print("CD: ", self.__serial_port.cd)
		
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
		if self.__receive_queue != None and not self.__receive_queue.empty():
			message = self.__receive_queue.get()
		return message
	
	
	def sendMessage(self, message):
		self.__serial_port.write(bytes(message + Transeiver.__FLUSH, encoding = 'utf-8'))
	
	def __del__(self):
		self.__fetchMessagesProcess.terminate()
		self.__serial_port.close()