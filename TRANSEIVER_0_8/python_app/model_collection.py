import serial
import multiprocessing
import time
import util 
import transceiver_commands as c
import threading
from ctypes import c_bool

class Command:
	@staticmethod
	def personal_message(ID, message, rx_address):
		if len(message) > c.MESSAGE_LENGTH:
			message = message[0:c.MESSAGE_LENGTH]
		null_byte_length = c.MESSAGE_LENGTH - len(message)
		null_bytes = chr(0) * null_byte_length
		return bytes(c.TRANSMIT + c.MESSAGE + ID + message + null_bytes + rx_address, encoding = "utf-8")
	
	@staticmethod
	def get_TX_address():
		return bytes(c.GET_TX_ADDRESS + c.FLUSH, encoding = "utf-8")
	
	@staticmethod
	def set_TX_address(address):
		return bytes(c.SET_TX_ADDRESS + address + c.FLUSH, encoding = "utf-8")
	
	@staticmethod
	def get_RX_address(pipe):
		return bytes(c.GET_RX_ADDRESS + pipe + c.FLUSH, encoding = "utf-8")
	
	@staticmethod
	def set_RX_address(address, pipe):
		return bytes(c.SET_RX_ADDRESS + pipe + address + c.FLUSH, encoding = "utf-8")
	
	@staticmethod
	def address_return(return_address):
		return bytes(c.TRANSMIT + c.ADDRESS_RETURN + return_address + c.FLUSH, encoding = "utf-8")
	
	@staticmethod
	def file_line(line):
		return bytes(c.TRANSMIT + c.FILE_LINE_SEND + line + c.FLUSH, encoding = "utf-8")
		
		
	
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
		self.communicationProcess = multiprocessing.Process(target = TransceiverInterface.communication, args = (self,SERIAL_PORT_NAME, BAUD_RATE, self.send_queue, self.receive_queue, self.state_queue, self.address_queue, self.success_queue,self.communication_process_on)) #maybe just make a new one
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
		self.send_queue.put(Command.get_TX_address())
		start = time.monotonic()
		while self.state_queue.empty():
			if time.monotonic() > start + 0.25:
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
			if time.monotonic() > start + 0.25:
				self.send_queue.put(Command.get_RX_address(pipe))
				start = time.monotonic()
		self.rx_address[ord(pipe)] = self.state_queue.get()
		
		while not self.state_queue.empty():
			self.state_queue.get()
		
		while not self.send_queue.empty():
			self.send_queue.get()
			
	
	def set_RX_address(self, address,pipe):
		self.send_queue.put(Command.set_RX_address(address, pipe))
		self.get_RX_address_from_node(pipe)

	@staticmethod
	def communication(obj, SERIAL_PORT_NAME, BAUD_RATE,send_queue, receive_queue, state_queue, address_queue, success_queue, process_on):         #gets the receiving messages in a parallel process # this gets put under cases
		ser = None
		process_on.value = True
		try:
			ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout = 0.10)
			while process_on.value:                   #maybe to improve reliability put them in seperate queues
				reading = ser.readline() #brrrreeeeaaaks here
				chunk_type = None
				
				if len(reading) > 0:
					#print("com:" + str(reading))
					chunk_type = reading[0:reading.index(ord(':'))].decode()
					
					
				if chunk_type == "ADDRESS":
					reading = obj.formatReceivedMessage(reading)    #should use obj instead since self makes it misleading
					address_queue.put(reading)
					
				elif chunk_type == "STATE":
					reading = obj.formatReceivedMessage(reading)
					state_queue.put(reading)
					
				elif chunk_type == "RECEIVED":
					reading = obj.formatReceivedMessage(reading)
					receive_queue.put(reading)
					
				elif chunk_type == "SUCCESS":
					reading = obj.formatReceivedMessage(reading)
					success_queue.put(reading)
					continue
				
				if(not send_queue.empty()):
					hmm = send_queue.get()
					#print(hmm)
					ser.write(hmm)
					
				#if "b''" == original:
				#	continue
				#print("\r" + reading + (" " * 50) + "\n")
				#print("\nEnter a message to write:",end="")
		except Exception as e:
			print(e)
		finally:
			ser.close()

	def formatReceivedMessage(self, message):
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
		self.receive_messages_queue = []
		self.sending_thread_on = False
		self.receiving_thread_on = False
		
		self.text_display = TextDisplayWrapper()   #have it by default be print in a different way
		
		self.sending_thread = threading.Thread(target = self.__sendThread)
		self.sending_thread.start()
		
		self.receiving_thread = threading.Thread(target = self.__receiveThread)
		self.receiving_thread.start()
		
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
			line = message[1:]
			self.transmit(Command.file_line(line))
			
		elif message[0] == "6":
			self.finding()
	
	def load(self, message,addresses = ["\x00!!"]): #can compartamentalize into a message class
		#need to make a base case
		self.pending_addresses_queue.append(addresses)
		message = self.rx_address[0] + "\t" + message
		chunks = util.messageChunks(message, c.MESSAGE_LENGTH)
		
		sent_message = chunks[0] + "\n"
		for i in range(1,len(chunks)):
			sent_message += " " * len(self.rx_address[0]) + "\t" + chunks[i]  + "\n"
		self.pending_message_queue.append(sent_message)
		
		chunks.append(chr(0))
		self.transmit_queue.append(chunks)
		
	def sendMessage(self, chunks):  # this will work by threads
		for ID in range(len(chunks)):
			if not self.transmit(Command.personal_message(str(ID), chunks[ID], self.rx_address[0])):
				return False #print failed if false
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
		while self.receiving_thread_on:
			message = self.receive()
			if message != None:
				ID = int(message[0])
				if ID == 0:
					personal_message_chunk = message[1:]
				elif len(message) != 1:
					personal_message_chunk = " " * 3 + "\t" + message[1:]
					
				if len(message) > 1 and ID > len(self.receive_messages_queue) - 1:
					self.receive_messages_queue.append(personal_message_chunk)
					
				elif len(message) == 1 and len(self.receive_messages_queue) != 0:
					self.text_display.write("\n".join(self.receive_messages_queue))
					self.receive_messages_queue.clear()
					
			
			
	
	def receive_message(self):
		pass
			
	
		
	def transmit(self, command): #this has a protocol to retransmit if fails through, yap I know its not using autoack
		if command[0] != ord(c.TRANSMIT):
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
	




		
		
			
		