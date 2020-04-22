from utility import util
import models.command_objects.transceiver_commands as c
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