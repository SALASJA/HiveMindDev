from utility import util 
import time
import threading
import models.command_objects.transceiver_commands as c
import os
from models.command_objects.command import Command
from models.transceiver_interfaces.transceiver_interface import TransceiverInterface
from models.data_objects.pending_message import PendingMessage
from models.data_objects.pending_file import PendingFile
from models.data_objects.receiving_message import ReceivingMessage
from models.data_objects.receiving_file import ReceivingFile	
from models.transceiver_interfaces.text_display_wrapper import TextDisplayWrapper

class MasterTransceiverInterface(TransceiverInterface):
	def __init__(self, SERIAL_PORT_NAME = None, BAUD_RATE = 9600):
		super().__init__(SERIAL_PORT_NAME, BAUD_RATE)
		self.nearby_nodes = []
		self.active_nodes = []
		
		self.receive_messages_queue = []
		self.receive_file_queue = []
		self.searching_running = False
		self.message_controller_created = False
		
		self.pending_loads = []
		self.pending_file_loads = []
		self.pending_message_objects = []   # this will replace some if the lists
		self.pending_file_objects = []
		self.receiving_message_objects = dict()
		self.receiving_file_objects = dict()
		self.new_status_messages = []
		
		self.text_display = TextDisplayWrapper()   #have it by default be print in a different way
		
		self.sending_thread = threading.Thread(target = self.__sendThread)
		self.receiving_thread = threading.Thread(target = self.__receiveThread)
		self.file_sending_thread  = threading.Thread(target = self.__fileSendThread)
		self.file_receiving_thread = threading.Thread(target = self.__fileReceiveThread)
		self.node_search_thread = threading.Thread(target = self.__finding)
		self.loading_file_thread = threading.Thread(target = self.__loading_file)
		self.loading_thread = threading.Thread(target = self.__loading)
		
		self.sending_thread_on = False
		self.receiving_thread_on = False
		self.file_sending_thread_on = False
		self.file_receiving_thread_on = False
		
		self.searching = False
		
		#self.start_threads() #maybe start when I open the port instead 
	
	def start_threads(self):
		self.receiving_thread.start()         #probably need to change to a process
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
			self.search()
			
		elif message[0] == "7":
			print(self.nearby_nodes)
			
	def load_file(self, filename, address = "\x00!!"):    #this stuff is annoying aaaaahhhhh
		self.pending_file_loads.append([filename,address])
		if not self.loading_file_thread.is_alive():
			self.loading_file_thread = threading.Thread(target = self.__loading_file)
			self.loading_file_thread.start()
	
	def __loading_file(self):
		while len(self.pending_file_loads) > 0:
			pending_file_args = self.pending_file_loads.pop(0)
			filename = pending_file_args[0]
			address = pending_file_args[1]
			self.pending_file_objects.append(PendingFile(filename, address))
			if not self.file_sending_thread.is_alive():
				self.file_sending_thread = threading.Thread(target = self.__fileSendThread)
				self.file_sending_thread.start()
		
		
				
		
	def load(self, message,addresses = ["\x00!!"]): #can compartamentalize into a message class
		self.pending_loads.append([message,addresses])
		if not self.loading_thread.is_alive():
			self.loading_thread = threading.Thread(target = self.__loading)
			self.loading_thread.start()
	
	def __loading(self):
		while len(self.pending_loads) > 0:
			pending_args = self.pending_loads.pop(0)
			message = pending_args[0]
			addresses = pending_args[1]
			self.pending_message_objects.append(PendingMessage(message, self.rx_address[0], addresses))
			if not self.sending_thread.is_alive():
				self.sending_thread = threading.Thread(target = self.__sendThread)
				self.sending_thread.start()
			
			
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
		while len(self.pending_message_objects) > 0:
			message_object = self.pending_message_objects.pop(0)
			message = message_object.get_message()
			addresses = message_object.get_target_addresses()
			chunks = message_object.get_chunks()
			for address in addresses:
				self.set_TX_address(address)
				if not self.sendMessage(chunks):
					message += address + "\t" + "<"* 6 + "FAILED" + ">" * 6 + "\n"
			self.text_display.write(message)
			self.new_status_messages.append(message)
				
	
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
						message = receiving_message_object.get_message()
						self.new_status_messages.append(message)
						self.text_display.write(message)
						addresses_to_remove.append(address)
				
				for address in addresses_to_remove:
					del self.receiving_message_objects[address]
						
					
					

	
	def __fileSendThread(self):
		while len(self.pending_file_objects) > 0:
			file_object = self.pending_file_objects.pop(0)
			address = file_object.get_target_address()
			chunks = file_object.get_chunks()
			filename = file_object.get_filename()
			self.set_TX_address(address)
			status = ""
			if not self.sendFile(chunks):
				status = " " * 3 + "\t" + "<<<<<" + filename + " FAILED>>>>>>"
			else:
				status = " " * 3 + "\t" + filename + " SENT!"
			self.text_display.write(status)
			self.new_status_messages.append(status)
	
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
					print("hmmmmmm: ", name_bytes)
					while i < len(name_bytes) and name_bytes[i] != 0:
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
						directory = os.getcwd()
						file = open(directory + "/received_" + filename, "wb")
						filebytes = receiving_file_object.get_bytes()
						file.write(filebytes)
						file.close()
						self.new_status_messages.append("   \t" + filename + " written\n")
						print("   \t" + filename + " written\n")
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
	
	def search(self):
		if not self.node_search_thread.is_alive():
			self.node_search_thread = threading.Thread(target = self.__finding)
			self.node_search_thread.start()
			
	
	def __finding(self):  #gonna modify the finding process
		self.searching = True
		self.nearby_nodes.clear()
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
		
			
		for address in addresses:
			if address not in self.active_nodes:
				self.nearby_nodes.append(address)
		
		self.searching = False
	
	def get_nearby_nodes(self):
		return self.nearby_nodes
	
	def nodes_nearby(self):
		return len(self.nearby_nodes) > 0
	
	def set_active_nodes(self, nodes):
		for node in nodes:
			if node not in self.active_nodes:
				self.active_nodes.append(node)
	
	def setTextDisplay(self, display):
		self.text_display = TextDisplayWrapper(display)
	
	def isMessageControllerCreated(self):
		return self.message_controller_created
	
	def setMessageControllerCreated(self, value):
		self.message_controller_created = value
	
	def is_searching(self):
		return self.searching
	
	
	def new_status(self):
		if len(self.new_status_messages) == 0:
			return None
		return self.new_status_messages.pop(0)
	
	
	def close(self):
		self.file_receiving_thread_on = False
		self.receiving_thread_on = False
		super().close()
	
	def __del__(self):
		self.close()
		




	
	





		
		
			
		