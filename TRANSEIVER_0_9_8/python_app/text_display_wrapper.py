class TextDisplayWrapper:
	def __init__(self, display_object = None):
		self.display_object = display_object
	
	def write(self, message):
		if self.display_object != None: # is instance
			pass
		else:
			print("\r\n" + message)
			print("\nEnter a message to write:", end = "")
	
	def setDisplayObject(self, display_object):
		self.display_object = display_object