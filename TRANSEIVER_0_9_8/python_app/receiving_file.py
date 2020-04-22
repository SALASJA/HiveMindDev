import util
import transceiver_commands as c
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
			print("\rID0:",ID,"amount: ", self.current_amount, "\tlength: ",  self.amount, "\tpercentage: ", self.current_amount/self.amount * 100)
		elif ID == 1 and len(self.chunks) % 2 == 1:
			self.chunks.append(bytearray(data))
			self.current_amount += 1
			print("\rID1:",ID,"amount: ", self.current_amount, "\tlength: ",  self.amount, "\tpercentage: ", self.current_amount/self.amount * 100)
	
	def is_complete(self):
		return self.current_amount == self.amount
	
	def get_filename(self):
		return self.filename
	
	def get_bytes(self):
		filebytes = bytearray()
		for chunk in self.chunks:
			filebytes += chunk
		return filebytes