from command_object import CommandObject
class StateCommandObject(CommandObject):  #the way imma read the addresses in the arduino code different now
	
	def set_address_pipe(self, pipe):
		self.bits[1] = pipe
	
	def set_address(self, address):
		bit_index = 2
		for i in range(3):
			self.bits[bit_index] = address[i]
			bit_index += 1