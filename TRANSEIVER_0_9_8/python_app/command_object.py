class CommandObject:
	def __init__(self):
		self.bits = bytearray(32)
	
	def set_USART_mode(self, mode):
		self.bits[0] = mode
	
	def get_bits(self):
		return bytes(self.bits)