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
			
	
	def set_RX_address(self, address,pipe):
		self.send_queue.put(Command.set_RX_address(address, pipe))
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
					#print("FILELINE:",data[1:])
					file_queue.put(data[1:len(data) - 3]) #i have to modify this too but just gonna make messages work again then will optimize
				
			
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




class MasterTransceiverInterface(TransceiverInterface):
	def __init__(self, SERIAL_PORT_NAME = None, BAUD_RATE = 9600):
		super().__init__(SERIAL_PORT_NAME, BAUD_RATE)
		self.pending_message_queue = []
		self.pending_addresses_queue = []
		self.transmit_queue = []
		self.file_transmit_queue = []
		self.receive_messages_queue = []
		self.receive_file_queue = []
		self.sending_thread_on = False
		self.receiving_thread_on = False
		self.file_sending_thread_on = False
		self.file_receiving_thread_on = False
		self.pending_file_addresses_queue = []
		
		self.text_display = TextDisplayWrapper()   #have it by default be print in a different way
		
		self.sending_thread = threading.Thread(target = self.__sendThread)
		self.sending_thread.start()
		
		self.receiving_thread = threading.Thread(target = self.__receiveThread)
		self.receiving_thread.start()
		
		self.file_sending_thread  = threading.Thread(target = self.__fileSendThread)
		self.file_sending_thread.start()
		
		self.file_receiving_thread = threading.Thread(target = self.__fileReceiveThread)
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
			pipe = chr(int(message[1]))
			self.set_RX_address(address, pipe)
			
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
		self.pending_file_addresses_queue.append(address)
		file = open(filename, "rb")
		data = file.read()
		chunks = util.fileChunks(data,c.MESSAGE_LENGTH)
		if len(chunks) > 33038209969: #max file size send allowed 100 GB
			print("File too big")
		
		filename = bytearray(bytes(filename,encoding = "utf-8"))
		length = util.get_length_bytes(len(chunks))
		info_chunk = bytearray(length) + filename
		chunks.insert(0,info_chunk)
		self.file_transmit_queue.append(chunks)
				
		
	def load(self, message,addresses = ["\x00!!"]): #can compartamentalize into a message class
		#need to make a base case
		self.pending_addresses_queue.append(addresses)
		message = self.rx_address[0] + "\t" + message
		chunks = util.messageChunks(message, c.MESSAGE_LENGTH)
		
		sent_message = chunks[0] + "\n"
		for i in range(1,len(chunks)):
			sent_message += " " * len(self.rx_address[0]) + "\t" + chunks[i]  + "\n"
		self.pending_message_queue.append(sent_message)
		
		chunks.insert(0,chr(len(chunks)))
		self.transmit_queue.append(chunks)
		
	def sendMessage(self, chunks):  # this will work by threads
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
			if len(self.pending_message_queue) > 0:
				message = self.pending_message_queue.pop(0)
				addresses = self.pending_addresses_queue.pop(0)
				chunks = self.transmit_queue.pop(0)
				for address in addresses:
					self.set_TX_address(address)
					if not self.sendMessage(chunks):
						message += address + "\t" + "<"* 6 + "FAILED" + ">" * 6 + "\n"
				self.text_display.write(message)
	
	def __receiveThread(self):
		self.receiving_thread_on = True  #this can be grouped and chunked into message classes
		amount = 0
		length = 0
		chunks = []
		while self.receiving_thread_on:
			message = self.receive()
			if message != None:
				ID = message[0]
				text_message = ""
				
				i = 1
				while message[i] != 0:
					text_message += chr(message[i])
					i = i + 1
				
				if ID == 2:
					length = message[1]
				elif ID == 0 and len(chunks) % 2 == 0 and length != 0 and len(chunks) == 0:
					chunks.append(text_message)
					amount += 1
				elif ID == 0 and len(chunks) % 2 == 0 and length != 0 and len(chunks) > 0:
					chunks.append(" " * 3 + "\t" + text_message)
					amount += 1
				elif ID == 1 and len(chunks) % 2 == 1 and length != 0:
					chunks.append(" " * 3 + "\t" + text_message)
					amount += 1
				
				if amount == length:
					self.text_display.write("\n".join(chunks))
					chunks.clear()
					amount = 0
					length = 0
					
					

	
	def __fileSendThread(self):
		self.file_sending_thread_on = True
		while self.file_sending_thread_on:
			if len(self.file_transmit_queue) > 0: 
				address = self.pending_file_addresses_queue.pop(0)
				chunks = self.file_transmit_queue.pop(0)
				filename = chunks[0][5:].decode()
				self.set_TX_address(address)
				if not self.sendFile(chunks):
					self.text_display.write(" " * 3 + "\t" + "<<<<<" + filename + " FAILED>>>>>>")
				else:
					self.text_display.write(" " * 3 + "\t" + filename + " SENT!")
	
	def __fileReceiveThread(self):
		self.file_receiving_thread_on = True  #this can be grouped and chunked into message classes
		filename = None
		amount = 0
		length = 0
		chunks = []
		while self.file_receiving_thread_on:
			file_line = self.file_line_receive()
			if file_line != None:
				ID = file_line[0]
				data = file_line[1:]
			
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
					
				elif ID == 0 and len(chunks) % 2 == 0 and length != 0:
					chunks.append(bytearray(data))
					amount += 1
					print("ID0:",ID,"amount: ", amount, "\tlength: ",  length, "\tpercentage: ", amount/length * 100)
				elif ID == 1 and len(chunks) % 2 == 1 and length != 0:
					chunks.append(bytearray(data))
					amount += 1
					print("ID1:",ID,"amount: ", amount, "\tlength: ",  length, "\tpercentage: ", amount/length * 100)
			
				if amount == length:
					total_data = bytearray()
					for byte_arrays in chunks:
						total_data += byte_arrays
					file = open("received_" + filename,"wb")
					file.write(total_data)
					file.close()
					print("file_written***********************")
					chunks.clear()
					amount = 0
					length = 0
				
				
				
					
			
			
	
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
			#print("clearing")
		
		while not self.success_queue.empty(): # this success queue might need to be fixed longer
			self.success_queue.get()
			#print("clearing")
		"""
		if not success:
			print("message sent!")
		else:
			print("message fail")
		"""
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
	





		
		
			
		