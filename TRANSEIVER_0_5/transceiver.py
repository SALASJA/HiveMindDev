import serial
import multiprocessing
import time

class Transceiver:
	MESSAGING = 0
	SET_TX_ADDRESS = 1
	SET_RX_ADDRESS = 2
	GET_TX_ADDRESS = 3
	GET_RX_ADDRESS = 4
	TOGGLE_SUCCESS_MODE = 5
	GET_SUCCESS_MODE = 6
	TOGGLE_LED = 7
	FINDING = 8
	FLUSH = '\r'   #should use something different
	
	def __init__(self, SERIAL_PORT_NAME = None, BAUD_RATE = 9600): # there might need to be a node ID nodeid = A, and tx = 00000 and rx = 11111
		self.communicationProcess = None
		self.send_queue = None
		self.receive_queue = None
		self.state_queue = None
		self.address_queue = None
		self.file_queue = None
		self.success_queue = None
		if SERIAL_PORT_NAME != None:
			self.startCommunicationProcess(SERIAL_PORT_NAME, BAUD_RATE)

	
	def startCommunicationProcess(self, SERIAL_PORT_NAME, BAUD_RATE):
		self.receive_queue = multiprocessing.Queue()
		self.send_queue = multiprocessing.Queue()
		self.state_queue = multiprocessing.Queue()
		self.address_queue = multiprocessing.Queue()
		self.success_queue = multiprocessing.Queue()
		self.communicationProcess = multiprocessing.Process(target = Transceiver.communication, args = (self,SERIAL_PORT_NAME, BAUD_RATE, self.send_queue, self.receive_queue, self.state_queue, self.address_queue, self.success_queue)) #maybe just make a new one
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
				print("\r" + original + (" " * 50) + "\n")
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
				message = message[l:len(message) - 3]
			else:
				r = message.index('\\')
				message = message[l:r]
		except Exception as e:
			print(e)
			message = copy_of_message
		return message
			
	def receiveMessage(self):
		messages = None
		if self.receive_queue != None and not self.receive_queue.empty():
			message = self.receive_queue.get()
		return message
	
	def sendMessage(self, message):
		if  ord(message[0]) == Transceiver.MESSAGING:
			self.sendMediaMessage(message)
		elif ord(message[0]) == Transceiver.FINDING:
			self.finding(message[1:])
		else:
			self.send_queue.put(bytes(message + Transceiver.FLUSH,encoding = "utf-8"))
			
		
	def sendMediaMessage(self, message): #this has a protocol to retransmit if fails through, yap I know its not using autoack
		self.send_queue.put(bytes(message + Transceiver.FLUSH,encoding = "utf-8"))
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
	
	def finding(self, command):
		pass
				
		
	
	def __del__(self):
		self.communicationProcess.terminate()
		self.receive_queue.close()
		self.send_queue.close()
		self.state_queue.close()
		self.address_queue.close()
		self.file_queue.close()
		self.success_queue.close()


		
		
			
		