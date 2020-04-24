import serial
import multiprocessing
import time
import util 
import transceiver_commands as c
import threading
from ctypes import c_bool


MESSAGE = 0
STATE = 1
SUCCESS = 2
ADDRESS = 3
FILELINE = 4
"""optimize the class so this not up here"""

class CommandObject:
	def __init__(self):
		self.bits = bytearray(32)
	
	def set_USART_mode(self, mode):
		self.bits[0] = mode
	
	def get_bits(self):
		return bytes(self.bits)

class StateCommandObject(CommandObject):  #the way imma read the addresses in the arduino code different now
	
	def set_address_pipe(self, pipe):
		self.bits[1] = pipe
	
	def set_address(self, address):
		bit_index = 2
		for i in range(3):
			self.bits[bit_index] = address[i]
			bit_index += 1

class TransmitCommandObject(CommandObject):
	def set_WhenReceived_mode(self,mode):
		self.bits[1] = mode
		

class FindCommandObject(TransmitCommandObject):
	def set_source_address(self, address):
		bit_index = 2
		for i in range(3):
			self.bits[bit_index] = address[i]
			bit_index += 1
	

class MessageCommandObject(TransmitCommandObject):
	def set_message_id(self,ID):
		self.bits[2] = ID
	
	def set_message(self, message): #messages are now a length of 25
		if len(message) > c.MESSAGE_LENGTH:
			message = message[0:c.MESSAGE_LENGTH]
		bit_index = 3
		for i in range(len(message)):
			self.bits[bit_index] = message[i]
			bit_index += 1
	
	def set_source_address(self, address):
		bit_index = 29
		for i in range(3):
			self.bits[bit_index] = address[i]
			bit_index += 1
	
	
			
		

class Command:
	@staticmethod
	def personal_message(ID, message, rx_address): #this might be easier to fix
		command = MessageCommandObject()
		command.set_USART_mode(c.TRANSMIT)
		command.set_WhenReceived_mode(c.PERSONAL_MESSAGE)
		command.set_message_id(ID)
		command.set_message(bytes(message, encoding = "utf-8"))
		command.set_source_address(bytes(rx_address, encoding = "utf-8"))
		return command.get_bits()
		
	@staticmethod
	def get_TX_address():
		command = StateCommandObject()
		command.set_USART_mode(c.GET_TX_ADDRESS)
		return command.get_bits()
	
	@staticmethod
	def set_TX_address(address):
		command = StateCommandObject()
		command.set_USART_mode(c.SET_TX_ADDRESS)
		command.set_address(bytes(address, encoding = "utf-8"))
		return command.get_bits()
	
	@staticmethod
	def get_RX_address(pipe):
		command = StateCommandObject()
		command.set_USART_mode(c.GET_RX_ADDRESS)
		command.set_address_pipe(pipe)
		return command.get_bits()
	
	@staticmethod
	def set_RX_address(pipe, address):
		command = StateCommandObject()
		command.set_USART_mode(c.SET_RX_ADDRESS)
		command.set_address_pipe(pipe)
		command.set_address(bytes(address, encoding = "utf-8"))
		return	command.get_bits()
	
	@staticmethod
	def address_return(return_address):
		command = FindCommandObject()
		command.set_USART_mode(c.TRANSMIT)
		command.set_WhenReceived_mode(c.ADDRESS_RETURN)
		command.set_source_address(bytes(return_address, encoding = "utf-8"))
		return command.get_bits()
	
	@staticmethod
	def file_line(ID,line,rx_address):#fix in case line is too small
		command = MessageCommandObject()
		command.set_USART_mode(c.TRANSMIT)
		command.set_WhenReceived_mode(c.FILE_LINE_SEND)
		command.set_message_id(ID)
		command.set_message(line)
		command.set_source_address(bytes(rx_address, encoding = "utf-8"))
		return command.get_bits()

#add the new stuff as A seperate class and make TransceiverInterface a subclass of it

		
		
	
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
		start_time = time.monotonic()
		ser = None
		process_on.value = True
		try:
			ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout = 0)
			while process_on.value:                   #maybe to improve reliability put them in seperate queues
				data = TransceiverInterface.get_data(ser)		
				type = TransceiverInterface.get_type(data)
					
				if type == MESSAGE:
					print("MESSAGE: ", data[1:], "   time: ", time.monotonic() - start_time)
					receive_queue.put(data[1:])
					
				elif type == STATE:
					print("hmmmm", data[1:].decode())
					state_queue.put(data[1:].decode())
					
				elif type == SUCCESS:
					success_queue.put(data[1:].decode())
					
				elif type == ADDRESS:
					print("ADDRESS:", data[1:])
					
				elif type == FILELINE:
					print("FILELINE:",data[1:])
					file_queue.put(data[1:]) #i have to modify this too but just gonna make messages work again then will optimize
				
			
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


#make the pending message object soon
class PendingMessage:
	def __init__(self, message, source_address, target_addresses = ["\x00!!"]):
		self.source_address = source_address
		self.target_addresses = target_addresses
		message = source_address + "\t" + message
		self.chunks = util.messageChunks(message, c.MESSAGE_LENGTH)
		self.message = util.chunks_to_message(self.chunks) #adjust it for payload length maybe
		self.chunks.insert(0,chr(len(self.chunks)))
	
	def get_chunks(self):
		return self.chunks
	
	def get_source_address(self):
		return self.source_address
	
	def get_message(self):
		return self.message
	
	def get_target_addresses(self):
		return self.target_addresses

class PendingFile:
	def __init__(self, filename, target_address = "\x00!!"):
		self.target_address = target_address
		self.filename = filename
		file = open(filename, "rb")
		data = file.read()
		file.close()
		chunks = util.fileChunks(data,c.MESSAGE_LENGTH)
		if len(chunks) > 33038209969: #max file size send allowed 100 GB
			raise Exception("File too big")
			
		length = util.get_length_bytes(len(chunks))       
		info_chunk = bytearray(length) + bytearray(bytes(filename,encoding = "utf-8"))
		chunks.insert(0,info_chunk)
		self.chunks = chunks
	
	def get_filename(self):
		return self.filename
	
	def get_chunks(self):
		return self.chunks
	
	def get_target_address(self):
		return self.target_address

class ReceivingMessage:
	def __init__(self, amount):
		self.chunks = []
		self.amount = amount
		self.current_amount = 0
		
	def add_chunk(self, chunk):
		ID = chunk[2]
		message_bytes = chunk[3:29]
		
		text_message = ""
		
		i = 0
		while i < len(message_bytes) and message_bytes[i] != 0:
			text_message += chr(message_bytes[i])
			i = i + 1
		
		print("text_message: ", text_message)
			
		if ID == 0 and len(self.chunks) % 2 == 0  and len(self.chunks) == 0:
			self.chunks.append(text_message)
			self.current_amount += 1
		elif ID == 0 and len(self.chunks) % 2 == 0  and len(self.chunks) > 0:
			self.chunks.append(" " * 3 + "\t" + text_message)
			self.current_amount += 1
		elif ID == 1 and len(self.chunks) % 2 == 1:
			self.chunks.append(" " * 3 + "\t" + text_message)
			self.current_amount += 1
	
	def is_complete(self):
		return self.current_amount == self.amount
	
	def get_message(self):
		return "\n".join(self.chunks)

class ReceivingFile:
	def __init__(self,amount, filename):
		self.amount = amount
		self.current_amount = 0
		self.filename = filename
		self.chunks = []

	def add_chunk(self, chunk):
		ID = chunk[2]
		data = chunk[3:29]
		if ID == 0 and len(self.chunks) % 2 == 0:
			self.chunks.append(bytearray(data))
			self.current_amount += 1
			print("ID0:",ID,"amount: ", self.current_amount, "\tlength: ",  self.amount, "\tpercentage: ", self.current_amount/self.amount * 100)
		elif ID == 1 and len(self.chunks) % 2 == 1:
			self.chunks.append(bytearray(data))
			self.current_amount += 1
			print("ID1:",ID,"amount: ", self.current_amount, "\tlength: ",  self.amount, "\tpercentage: ", self.current_amount/self.amount * 100)
	
	def is_complete(self):
		return self.current_amount == self.amount
	
	def get_filename(self):
		return self.filename
	
	def get_bytes(self):
		filebytes = bytearray()
		for chunk in self.chunks:
			filebytes += chunk
		return filebytes
		
		
		
		
		
		


class MasterTransceiverInterface(TransceiverInterface):
	def __init__(self, SERIAL_PORT_NAME = None, BAUD_RATE = 9600):
		super().__init__(SERIAL_PORT_NAME, BAUD_RATE)
		
		self.receive_messages_queue = []
		self.receive_file_queue = []
		
		
		self.pending_message_objects = []   # this will replace some if the lists
		self.pending_file_objects = []
		self.receiving_message_objects = dict()
		self.receiving_file_objects = dict()
		
		self.text_display = TextDisplayWrapper()   #have it by default be print in a different way
		
		self.sending_thread = threading.Thread(target = self.__sendThread)
		self.receiving_thread = threading.Thread(target = self.__receiveThread)
		self.file_sending_thread  = threading.Thread(target = self.__fileSendThread)
		self.file_receiving_thread = threading.Thread(target = self.__fileReceiveThread)
		
		self.sending_thread_on = False
		self.receiving_thread_on = False
		self.file_sending_thread_on = False
		self.file_receiving_thread_on = False
		
		self.start_threads()
	
	def start_threads(self):
		self.sending_thread.start()
		self.receiving_thread.start()
		self.file_sending_thread.start()
		self.file_receiving_thread.start()
		
	def command_line_send(self, message):
		if message[0] == "0":
			#ID = message[1]
			message = message.split(",")
			personal_message = message[0][1:]
			addresses = None
			if len(message) > 1:
				addresses = message[1:]
				self.load(personal_message, addresses)
			else:
				self.load(personal_message)
			
		elif message[0] == "1":
			address = message[1:]
			self.set_TX_address(address)
			
		elif message[0] == "2":
			address = message[2:]
			pipe = int(message[1])
			self.set_RX_address(pipe, address)
			
		elif message[0] == "3":
			print(self.get_TX_address())
			
		elif message[0] == "4":
			pipe = int(message[1])
			print(self.get_RX_address(pipe))
			
		elif message[0] == "5":
			file = message[1:]
			self.load_file(file)
			
		elif message[0] == "6":
			self.finding()
			
	def load_file(self, filename, address = "\x00!!"):    #this stuff is annoying aaaaahhhhh
		self.pending_file_objects.append(PendingFile(filename, address))
		
				
		
	def load(self, message,addresses = ["\x00!!"]): #can compartamentalize into a message class
		self.pending_message_objects.append(PendingMessage(message, self.rx_address[0], addresses))
		
		
		
	def sendMessage(self, chunks):  #this will work by threads
		STATE_ID = False
		for i in range(len(chunks)): ####error here because adding extra bytes by mistake
			if i == 0:
				if not self.transmit(Command.personal_message(2, chunks[i], self.rx_address[0])):
					return False #print failed if false
			else:
				if not self.transmit(Command.personal_message(int(STATE_ID), chunks[i], self.rx_address[0])):
					return False #print failed if false
				STATE_ID = not STATE_ID
		return True
		
	
	def sendFile(self,chunks):
		STATE_ID = False
		for i in range(len(chunks)): #error here too
			if i == 0:
				if not self.transmit(Command.file_line(2, chunks[i], self.rx_address[0])):
					return False
			else:
				if not self.transmit(Command.file_line(int(STATE_ID),chunks[i], self.rx_address[0])):
					return False
				STATE_ID = not STATE_ID
		return True
		
	
	def __sendThread(self):
		self.sending_thread_on = True
		while self.sending_thread_on:
			if len(self.pending_message_objects) > 0:
				message_object = self.pending_message_objects.pop(0)
				message = message_object.get_message()
				addresses = message_object.get_target_addresses()
				chunks = message_object.get_chunks()
				for address in addresses:
					self.set_TX_address(address)
					if not self.sendMessage(chunks):
						message += address + "\t" + "<"* 6 + "FAILED" + ">" * 6 + "\n"
				self.text_display.write(message)
				
	
	def __receiveThread(self):
		self.receiving_thread_on = True  #this can be grouped and chunked into message classes
		while self.receiving_thread_on:
			message = self.receive()
			if message != None:
				ID = message[2]
				address = message[29:].decode() #only acceptable addresses allowed?
				
				if ID == 2:
					amount = message[3]
					self.receiving_message_objects[address] = ReceivingMessage(amount)
				else:
					self.receiving_message_objects[address].add_chunk(message)
					

				addresses_to_remove = []
				for address in self.receiving_message_objects:
					receiving_message_object = self.receiving_message_objects[address]
					if receiving_message_object.is_complete():
						self.text_display.write(receiving_message_object.get_message())
						addresses_to_remove.append(address)
				
				for address in addresses_to_remove:
					del self.receiving_message_objects[address]
						
					
					

	
	def __fileSendThread(self):
		self.file_sending_thread_on = True
		while self.file_sending_thread_on:
			if len(self.pending_file_objects) > 0:
				file_object = self.pending_file_objects.pop(0)
				address = file_object.get_target_address()
				chunks = file_object.get_chunks()
				filename = file_object.get_filename()
				self.set_TX_address(address)
				if not self.sendFile(chunks):
					self.text_display.write(" " * 3 + "\t" + "<<<<<" + filename + " FAILED>>>>>>")
				else:
					self.text_display.write(" " * 3 + "\t" + filename + " SENT!")
	
	def __fileReceiveThread(self):
		self.file_receiving_thread_on = True  #this can be grouped and chunked into message classes
		while self.file_receiving_thread_on:
			file_line = self.file_line_receive()
			if file_line != None:
				ID = file_line[2]
				data = file_line[3:29]
				address = file_line[29:].decode()
				if ID == 2:
					length_bytes = data[0:5]
					length = util.get_amount(length_bytes) #call this get length soon
					name_bytes = data[5:]
					name = ""
					i = 0
					while name_bytes[i] != 0:
						name += chr(name_bytes[i])
						i = i + 1
				
					filename = name
					self.receiving_file_objects[address] = ReceivingFile(length,filename)
				else:
					self.receiving_file_objects[address].add_chunk(file_line)
					
				addresses_to_remove = []
				for address in self.receiving_file_objects:
					receiving_file_object = self.receiving_file_objects[address]
					if receiving_file_object.is_complete():
						filename = receiving_file_object.get_filename()
						file = open("received_" + filename, "wb")
						filebytes = receiving_file_object.get_bytes()
						file.write(filebytes)
						file.close()
						print("file_written***********************")
						addresses_to_remove.append(address)
				
				
				for address in addresses_to_remove:
					del self.receiving_file_objects[address]

				
				
				
					
			
			
	
	def receive_message(self):
		pass
			
	
		
	def transmit(self, command): #this has a protocol to retransmit if fails through, yap I know its not using autoack
		if command[0] != c.TRANSMIT:
			return
			
		self.send_queue.put(command)
		
		start = time.monotonic()
		interval = start
		success = False
		
		while not self.success_queue.empty(): # this success queue might need to be fixed longer
			self.success_queue.get()
			
		while time.monotonic() < start + 15:
			if time.monotonic() > interval + 1:
				print("sent again")
				self.send_queue.put(command)
				interval = time.monotonic()
				
			if not self.success_queue.empty():
				success = True
				self.success_queue.get()   #sometimes wrong here
				break   
				
		while not self.send_queue.empty():
			self.send_queue.get()
		
		while not self.success_queue.empty(): # this success queue might need to be fixed longer
			self.success_queue.get()

		return success
		
	
	def finding(self):  #gonna modify the finding process
		self.send_queue.put(Command.set_TX_address(c.FINDING_ADDRESS))
		start = time.monotonic()
		interval = start
		addresses = []
		self.send_queue.put(Command.address_return(self.rx_address[0]))
		while time.monotonic() < start + 15:
			if time.monotonic() > interval + 0.10:
				print("searching")
				self.send_queue.put(Command.address_return(self.rx_address[0]))
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
		
		
		self.send_queue.put(Command.set_TX_address(self.tx_address))
		#cycle through address that return a success and there is our list
		
			
		return addresses
	
	def setTextDisplay(self, display):
		self.text_display = TextDisplayWrapper(display)
	
	def close(self):
		super().close()
		print("hello")
		self.sending_thread_on = False
		for i in range(10):
			print("waiting")
		self.sending_thread.join()
		
		self.receiving_thread_on = False
		for i in range(10):
			print("waiting")
		self.receiving_thread.join()
	
	def __del__(self):
		self.close()
		



class TextDisplayWrapper:
	def __init__(self, display_object = None):
		self.display_object = display_object
	
	def write(self, message):
		if self.display_object != None: # is instance
			pass
		else:
			print("\r\n" + message)
			print("\nEnter a message to write:", end = "")
	
	def setDisplayObject(self, display_object):
		self.display_object = display_object
	





		
		
			
		