from command_object import CommandObject
class TransmitCommandObject(CommandObject):
	def set_WhenReceived_mode(self,mode):
		self.bits[1] = mode