from models.command_objects.transmit_command_object import TransmitCommandObject
class FindCommandObject(TransmitCommandObject):
	def set_source_address(self, address):
		bit_index = 2
		for i in range(3):
			self.bits[bit_index] = address[i]
			bit_index += 1