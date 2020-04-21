import util
import transceiver_commands as c
#make the pending message object soon
class PendingMessage:
	def __init__(self, message, source_address, target_addresses = ["\x00!!"]):
		self.source_address = source_address
		self.target_addresses = target_addresses
		message = source_address + "\t" + message
		self.chunks = util.messageChunks(message, c.MESSAGE_LENGTH)
		self.message = util.chunks_to_message(self.chunks) #adjust it for payload length maybe  and adjust it to have flatter looking messages
		self.chunks.insert(0,chr(len(self.chunks)))
	
	def get_chunks(self):
		return self.chunks
	
	def get_source_address(self):
		return self.source_address
	
	def get_message(self):
		return self.message
	
	def get_target_addresses(self):
		return self.target_addresses