import tkinter as tk
from view_collection import SettingsView, AddConnectionView, MessageView, HistoryView
from functools import partial
import threading
import glob

class Controller:
	
	def __init__(self, view, model):
		self.view = view
		self.model = model
		self.view.construct_view()
		self.construct_subcontrollers()
		self.set_events()
	
	def construct_subcontrollers(self):
		settings_view = self.view.getSettingsView()
		settings_view.setMainView(self.view)
		SettingsController(settings_view, self.model)
		
	def set_events(self):
		dropmenu = self.view.getWidget("Application_dropmenu")
		dropmenu.entryconfig(0, command = self.open_settings)
		dropmenu.entryconfig(1, command = self.open_add_connection)
		dropmenu.entryconfig(2, command = self.open_history)
		window = self.view.getWidget("window")
		
	
	def open_settings(self):
		settings_view = self.view.getSettingsView()
		settings_view.show()
	
	def open_add_connection(self):
		add_connection_view = self.view.getAddConnectionView()
		add_connection_view.show() #refresh
		add_connection_view.setMainView(self.view)
		AddConnectionController(add_connection_view, self.model)
		
	def open_history(self):
		add_history_view = self.view.getHistoryView()
		add_history_view.show()
		add_history_view.setMainView(self.view)
		HistoryController(add_history_view, self.model)
		
	
	def add_connection(self):
		add_connection_window = tk.Toplevel()
		add_connection_view = AddConnectionView(add_connection_window)
		
		self.view.setAddConnectionView(add_connection_view)
		add_connection_view.setMainView(self.view)
		
		AddConnectionController(add_connection_view, self.model)
	
		

class HistoryController:
	def __init__(self,view, model):
		self.view = view
		self.model = model
		self.set_events()
		
	def set_events(self):
		history_label = self.view.getWidget("history_label")
		
		
		
		
class SettingsController:
	def __init__(self,view, model):
		self.view = view
		self.model = model
		self.set_events()
	
		
	
	def __usePort(self):
		self.model.closeSerialPort()
		label = self.view.getMainViewWidget("statusbar")
		port_choice = self.view.getWidget("port_choice")
		serial_port_name = port_choice.get()
		if serial_port_name != "None selected":
			label["text"] = "Connected on " + serial_port_name
			self.model.openSerialPort(serial_port_name)
			
	
	def __updatePortList(self):
		serialPortOptionMenu = self.view.getWidget("serialPortOptionMenu")
		port_choice = self.view.getWidget("port_choice")
		serial_ports = glob.glob("/dev/tty.wchusbserial*") + glob.glob("/dev/tty.usbserial*") + glob.glob("COM*")  
		if len(serial_ports) == 0:
			self.model.closeSerialPort()
		menu = serialPortOptionMenu.children['menu']
		menu.delete(0,END)
		serial_ports.insert(0, "None selected")
		for val in serial_ports:
			menu.add_command(label=val,command=lambda v=port_choice,l=val:v.set(l))
		port_choice.set(serial_ports[0])		
	
	def set_events(self):
		port_refresh_button = self.view.getWidget("port_refresh_button")
		port_refresh_button["command"] = self.__updatePortList
		
		port_select_button = self.view.getWidget("port_select_button")
		port_select_button["command"] = self.__usePort
	
		


class AddConnectionController: #NOW UPDATEING THIS
	def __init__(self,view, model):
		self.view = view
		self.model = model
		self.set_events()
	
	def look_for_connections(self):
		statusbar = self.view.getParentViewWidget("statusbar")
		if statusbar["text"] != "No MasterNode Connection":
			toplevel_add_connection_window = self.view.getWidget("toplevel_add_connection_window")
			toplevel_add_connection_window.title("SEARCHING")
			toplevel_add_connection_window.update()
			connections = self.model.findConnections()
			toplevel_add_connection_window.title("DONE SEARCHING")
			toplevel_add_connection_window.update()
			self.view.add_connections(connections)
			labels = self.view.getWidget("connections")
			for label in labels:
				label.bind("<Button-1>", self.select_connection)
		
		 
	
	def set_events(self):
		window = self.view.getWidget("widget_canvas")
		window.bind("<Key>", self.multiple)
		window.focus_set()
		select_button = self.view.getWidget("select_button")
		select_button["command"] = self.add_connections
		node_search_button = self.view.getWidget("node_search_button")
		node_search_button["command"] = self.look_for_connections
	
	def multiple(self, event):
		statusbar = self.view.getWidget("statusbar")
		if "Single Node Selection Mode" == statusbar["text"]:
			statusbar["text"] = "Multiple Node Selection Mode"
		elif "Multiple Node Selection Mode" == statusbar["text"]:
			statusbar["text"] = "Single Node Selection Mode"
	
	def select_connection(self, event):
		labels = self.view.getWidget("connections")
		statusbar = self.view.getWidget("statusbar")
		if "Single Node Selection Mode" == statusbar["text"]:
			for label in labels:
				label["bg"] = "white"
			
		label = event.widget
		label["bg"] = "light blue"	
		
	
	def add_connections(self):
		main_view = self.view.getMainView()
		message_view = main_view.getMessageView()
		connection_views = main_view.getConnectionViews()
		choices = self.view.getWidget("connections")
		for choice in choices:
			if choice["text"] not in connection_views and choice["bg"] == "light blue":
				main_view.add_connection(choice["text"])
				message_view.add_node_to_list(choice["text"])
				
		for connection_view_name in connection_views:
			view = connection_views[connection_view_name]
			view.setMainView(main_view)
			ConnectionController(view,self.model)
		
		


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
		print("hmmmm")
		#send_file_window = tk.Toplevel()
		#SendFileController(MessageView(send_file_window), self.model)
	
	def open_settings_window(self):
		print("hmmm")
		#settings_window = tk.Toplevel()
		#SettingsWindowController(settings_window, self.model)


class MessageController:
	def __init__(self, view, model):
		self.view = view
		self.model = model
		self.send_thread = None #i create the threads in the module
		self.receive_thread = None
		self.lock = threading.Lock()
		self.loop = False
		self.__setEventBindings()
		self.__run()
		
	
	def __run(self):
		self.receive_thread = threading.Thread(target = self.__getMessages, args = (self.lock,) )
		#self.receive_thread.setDaemon(True)
		self.receive_thread.start()
	
	def hide(self):
		window = self.view.getWidget("window")
		window.withdraw()
		if self.send_thread != None:
			self.send_thread.join()
		
		
	
	def __send_message(self, lock):
		message_input = self.view.getWidget("entry")#"message_input")
		message = message_input.get("1.0",tk.END)
		message = message.strip()
		addresses = self.view.getNodeList() #must load addresses as well onto model to make this affective      #set the address within the model i
		#self.__sending()
		text_widget = self.view.getWidget("text_widget")
		window = self.view.getWidget("window")
		for address in addresses:
			self.model.setSendingAddress(address)
			self.model.load(message)
			sent = self.model.send()
			while sent and not self.model.empty():
				sent = self.model.send()
		
		
		if not sent:
			message = self.model.getFailedMessage()
			lock.acquire()
			text_widget.config(state="normal")
			text_widget.insert(tk.END,message + "  FAILED\n")
			text_widget.config(state=tk.DISABLED)
			lock.release()
			self.model.setMessageLastSent("")
			return
	
		if self.model.empty():
			message = self.model.getMessageLastSent()
			lock.acquire()
			text_widget.config(state="normal")
			text_widget.insert(tk.END,message + "\n")
			text_widget.config(state=tk.DISABLED)
			lock.release()
			self.model.setMessageLastSent("")
		
		
		
			
		
		
		
		
	"""
	def __send_message(self):
		message_input = self.view.getWidget("entry")#"message_input")
		message = message_input.get("1.0",tk.END)
		message = message.strip()
		node_list = self.view.getNodeList() #must load addresses as well onto model to make this affective
		addresses = []
		for node in node_list:
			var = node[0]
			if var.get() == 1:
				addresses.append(node[1]["text"])
		
		self.model.load_addresses(addresses)
		#self.model.setSendingAddress(address)
		self.model.load(message)
		self.__sending()
	"""
	
	def __sending(self):
		text_widget = self.view.getWidget("text_widget")
		window = self.view.getWidget("window")
		sent = self.model.send()
		
		if not sent:
			text_widget.config(state="normal")
			message = self.model.getFailedMessage()
			text_widget.insert(tk.END,message + "  FAILED\n")
			text_widget.config(state=tk.DISABLED)
			self.model.setMessageLastSent("")
			return
		
		if not self.model.empty():   #here do something related to the addresses
			window.after(10, self.__sending)
		else:
			text_widget.config(state="normal")
			message = self.model.getMessageLastSent()
			text_widget.insert(tk.END,message + "\n")
			text_widget.config(state=tk.DISABLED)
			self.model.setMessageLastSent("")
			
			
				
	
	def __getMessages(self, lock):
		self.loop = True
		while self.loop:
			message = self.model.receive()
			if message != None:
				text_widget = self.view.getWidget("text_widget")
				lock.acquire()
				text_widget.config(state="normal")
				text_widget.insert(tk.END, message + "\n")
				text_widget.config(state=tk.DISABLED)
				lock.release()
		#window = self.view.getWidget("window")
		#window.after(10, self.__getMessages)
		
	
	def __clearTextWidget(self):
		self.model.resetMessageNumber()
		text_widget = self.view.getWidget("text_widget")
		self.lock.acquire()
		text_widget.config(state="normal")
		text_widget.delete("1.0", tk.END)
		text_widget.config(state=tk.DISABLED)
		self.lock.release()
	
	def __send_message_thread(self):
		if self.send_thread != None:
			self.send_thread.join()
		self.send_thread = threading.Thread(target = self.__send_message, args = (self.lock,))
		self.send_thread.start()
		
		
	def __setEventBindings(self):
		
		send_button = self.view.getWidget("send_button")
		send_button["command"] = self.__send_message_thread
		
		clear_button = self.view.getWidget("clear_button")
		clear_button["command"] = self.__clearTextWidget
		
		window = self.view.getWidget("window")
		window.protocol('WM_DELETE_WINDOW', self.hide)
	
	def __del__(self):
		self.loop = False
		if self.send_thread != None:
			print("close send thread")
			try:
				self.send_thread.join()
			except:
				pass
				
		if self.receive_thread != None:
			print("close receive thread")
			try:
				self.receive_thread.join()
			except:
				pass

		
		
		
		
		
		
		
		
		
		
		
		
		
