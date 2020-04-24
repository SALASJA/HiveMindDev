from controllers.message_controller import MessageController
from tkinter import filedialog
class ConnectionController:
	def __init__(self, view, model):
		self.view = view
		self.model = model
		self.view.constructLook()
		self.set_events()
	
	def set_events(self):
		removebutton = self.view.getWidget("removebutton")
		removebutton["command"] = self.__del__
		
		messagebutton = self.view.getWidget("message_button")
		messagebutton["command"] = self.open_message_window
		
		databutton = self.view.getWidget("data_button")
		databutton["command"] = self.open_data_window
		
		filebutton = self.view.getWidget("file_button")
		filebutton["command"] = self.open_send_file_window
		
		settings_button = self.view.getWidget("settings_button")
		settings_button["command"] = self.open_settings_window
	
	def __del__(self):
		main_view = self.view.getMainView()
		main_view.remove_connection(self.view.getName()) #gets destroyed when __del__ called anyway
		message_view = main_view.getMessageView()
		message_view.remove_node_from_list(self.view.getName())
		#self.model.removeConnection(self.view.getName())
	
	def getViewName(self):
		return self.view.getName()
	
	#open window must add edits
	def open_message_window(self):
		main_view = self.view.getMainView()
		message_view = main_view.getMessageView()
		if not self.model.isMessageControllerCreated():
			MessageController(message_view, self.model)
			self.model.setMessageControllerCreated(True)
		message_view.show()
		
	def open_data_window(self):
		print("hmmmm")
		#data_window = tk.Toplevel()
		#DataController(MessageView(message_window), self.model)
	
	def open_send_file_window(self):
		filename = filedialog.askopenfilename(initialdir = "/",title = "Select file" )
		self.model.load_file(filename)
		#send_file_window = tk.Toplevel()
		#SendFileController(MessageView(send_file_window), self.model)
	
	def open_settings_window(self):
		print("hmmm")
		#settings_window = tk.Toplevel()
		#SettingsWindowController(settings_window, self.model)