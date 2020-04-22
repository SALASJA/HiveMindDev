import models.command_objects.transceiver_commands as c
from models.command_objects.transmit_command_object import TransmitCommandObject
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