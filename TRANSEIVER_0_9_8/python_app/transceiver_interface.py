import time
import serial
import multiprocessing
from ctypes import c_bool
from command import Command
class TransceiverInterface: #rather than as static it should be kept in a seperate thing
	
	def __init__(self, SERIAL_PORT_NAME = None, BAUD_RATE = 9600): # there might need to be a node ID nodeid = A, and tx = 00000 and rx = 11111
		self.communicationProcess = None
		self.communication_process_on = multiprocessing.Value(c_bool, False)
		self.send_queue = None
		self.receive_queue = None
		self.state_queue = None
		self.address_queue = None
		self.file_queue = None
		self.success_queue = None
		self.rx_address = [0,0,0,0,0,0]
		self.tx_address = None
		#self.close = process.
		if SERIAL_PORT_NAME != None:
			self.startCommunicationProcess(SERIAL_PORT_NAME, BAUD_RATE)

	
	def startCommunicationProcess(self, SERIAL_PORT_NAME, BAUD_RATE = 9600):
		self.receive_queue = multiprocessing.Queue()
		self.send_queue = multiprocessing.Queue()
		self.state_queue = multiprocessing.Queue()
		self.address_queue = multiprocessing.Queue()
		self.success_queue = multiprocessing.Queue()
		self.file_queue = multiprocessing.Queue()
		self.communicationProcess = multiprocessing.Process(target = TransceiverInterface.communication, args = (SERIAL_PORT_NAME, BAUD_RATE, self.send_queue, self.receive_queue, self.state_queue, self.address_queue, self.success_queue, self.file_queue, self.communication_process_on)) #maybe just make a new one
		self.communicationProcess.start()
		self.get_TX_address_from_node()
		self.get_RX_address_from_node(0)
		self.get_RX_address_from_node(1)
		self.get_RX_address_from_node(2)
		self.get_RX_address_from_node(3)
		self.get_RX_address_from_node(4)
		self.get_RX_address_from_node(5)
		
	
	def stopCommunicationProcess(self):
		pass
		
	def get_TX_address(self):
		return self.tx_address
	
	def get_TX_address_from_node(self):
		self.send_queue.put(Command.get_TX_address())
		start = time.monotonic()
		while self.state_queue.empty():
			if time.monotonic() > start + 0.30:
				self.send_queue.put(Command.get_TX_address())
				start = time.monotonic()
		self.tx_address = self.state_queue.get()
		#print("setting address success: ", self.tx_address)
		while not self.state_queue.empty():
			self.state_queue.get()
		
		while not self.send_queue.empty():
			self.send_queue.get()
	
	def set_TX_address(self, address):
		#print("setting address: ", address)
		self.send_queue.put(Command.set_TX_address(address))
		self.get_TX_address_from_node()
		
	
	def get_RX_address(self, pipe):
		return self.rx_address[pipe]
	
	def get_RX_address_from_node(self, pipe):
		self.send_queue.put(Command.get_RX_address(pipe))
		start = time.monotonic()
		while self.state_queue.empty() :
			if time.monotonic() > start + 0.30:
				self.send_queue.put(Command.get_RX_address(pipe))
				start = time.monotonic()
		self.rx_address[pipe] = self.state_queue.get()
		
		while not self.state_queue.empty():
			self.state_queue.get()
		
		while not self.send_queue.empty():
			self.send_queue.get()
			
	
	def set_RX_address(self, pipe,address):
		self.send_queue.put(Command.set_RX_address(pipe, address))
		self.get_RX_address_from_node(pipe)
	
	#its now function just need to add stuff
	@staticmethod
	def communication(SERIAL_PORT_NAME, BAUD_RATE, send_queue, receive_queue, state_queue, address_queue, success_queue, file_queue, process_on):         #gets the receiving messages in a parallel process # this gets put under cases
		MESSAGE = 0
		STATE = 1
		SUCCESS = 2
		ADDRESS = 3
		FILELINE = 4
		start_time = time.monotonic()
		ser = None
		process_on.value = True
		try:
			ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout = 0)
			while process_on.value:                   #maybe to improve reliability put them in seperate queues
				data = TransceiverInterface.get_data(ser)		
				type = TransceiverInterface.get_type(data)
					
				if type == MESSAGE:
					#print("MESSAGE: ", data[1:], "   time: ", time.monotonic() - start_time)
					receive_queue.put(data[1:])
					
				elif type == STATE:
					#print("hmmmm", data[1:].decode())
					state_queue.put(data[1:].decode())
					
				elif type == SUCCESS:
					success_queue.put(data[1:].decode())
					
				elif type == ADDRESS:
					print("ADDRESS:", data[3:])
					try:
						data = str(data)
						address_queue.put(data[18:len(data) - 2])
					except:
						pass
				elif type == FILELINE:
					#print("FILELINE:",data[1:])
					file_queue.put(data[1:]) #i have to modify this too but just gonna make messages work again then will optimize
				elif len(data) > 0:
						print("hmmmm not good:", data)
				
			
				if not send_queue.empty():
					bits = send_queue.get()
					#print("BITSEND: ", bits)
					ser.write(bits)
				
		except Exception as e:
			print("ERROR: ", e)
		finally:
			ser.close()
	
	@staticmethod
	def get_data(ser):
		data = bytearray()
		byte = ser.read()

		if len(byte) > 0:
			length = byte[0]
			#print("byte: ", byte)
			i = 0
			while i < length:
				byte = ser.read()
				if len(byte) > 0:
					#print("byte: ", byte)
					data.append(byte[0])
					i = i + 1
		return data
	
	@staticmethod
	def get_type(data):
		type = None
		if len(data) > 0:
			type = data[0]
		return type
	
	
	
	@staticmethod
	def formatReceivedMessage(message):
		l = message.index(ord(':')) + 1
		message = message[l : len(message) - 1]
		copy_of_message = message
		try:                                          #if you remove the try except and type clear, the INVALID state message will cause reading.index(':') to throw an exception
			message = message.decode()
		except Exception as e:
			message = str(copy_of_message)
		return message
			
	def receive(self):
		message = None
		if self.receive_queue != None and not self.receive_queue.empty():
			message = self.receive_queue.get()
		return message
	
	def file_line_receive(self):
		file_line = None
		if self.file_queue != None and not self.file_queue.empty():
			file_line = self.file_queue.get()
		return file_line
	
	
	def send(self, command):
		self.send_queue.put(command)

	def close(self):
		if self.communicationProcess != None:
			self.communication_process_on.value = False
			for i in range(10):
				print("closeing")
			self.communicationProcess.join()
			self.communicationProcess.terminate()
		
		if self.receive_queue != None:
			self.receive_queue.close()
		
		if self.send_queue != None:
			self.send_queue.close()
		
		if self.state_queue != None:
			self.state_queue.close()
		
		if self.address_queue != None:
			self.address_queue.close()
		
		if self.file_queue != None:
			self.file_queue.close()
		
		if self.success_queue != None:
			self.success_queue.close()
	
	def __del__(self):
		self.close()
