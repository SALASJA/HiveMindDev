from utility import util
import models.command_objects.transceiver_commands as c
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
		
		#print("text_message: ", text_message)
			
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
		message = "\n".join(self.chunks)
		return message + "\n"