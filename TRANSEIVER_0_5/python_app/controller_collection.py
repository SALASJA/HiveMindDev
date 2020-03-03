import tkinter as tk
from view_collection import SettingsView, AddConnectionView, MessageView
from functools import partial
import threading
import glob

class Controller:
	def __init__(self, view, model):
		self.view = view
		self.model = model
		self.view.construct_view()
		self.set_events()
	
	def set_events(self):
		dropmenu = self.view.getWidget("Application_dropmenu")
		dropmenu.entryconfig(0, command = self.settings)
		dropmenu.entryconfig(1, command = self.add_connection)
	
	def settings(self):
		settings_window = tk.Toplevel()
		SettingsController(SettingsView(settings_window, self.view),self.model)
	
	def add_connection(self):
		add_connection_window = tk.Toplevel()
		AddConnectionController(AddConnectionView(add_connection_window, self.view), self.model)


class SettingsController:
	def __init__(self,view, model):
		self.view = view
		self.model = model
		self.__setEventBindings()
	
		
	
	def __usePort(self):
		self.model.closeSerialPort()
		label = self.view.getParentViewWidget("statusbar")
		port_choice = self.view.getWidget("port_choice")
		serial_port_name = port_choice.get()
		if serial_port_name != "None selected":
			label["text"] = "Connected on " + serial_port_name
			self.model.openSerialPort(serial_port_name)
			
	
	def __updatePortList(self):
		serialPortOptionMenu = self.view.getWidget("serialPortOptionMenu")
		port_choice = self.view.getWidget("port_choice")
		serial_ports = glob.glob("/dev/tty.wchusbserial*") + glob.glob("/dev/tty.usbserial*") + glob.glob("COM5")
		if len(serial_ports) == 0:
			self.model.closeSerialPort()
		menu = serialPortOptionMenu.children['menu']
		menu.delete(0,END)
		serial_ports.insert(0, "None selected")
		for val in serial_ports:
			menu.add_command(label=val,command=lambda v=port_choice,l=val:v.set(l))
		port_choice.set(serial_ports[0])		
	
	def __setEventBindings(self):
		port_refresh_button = self.view.getWidget("port_refresh_button")
		port_refresh_button["command"] = self.__updatePortList
		
		port_select_button = self.view.getWidget("port_select_button")
		port_select_button["command"] = self.__usePort


class AddConnectionController:
	def __init__(self,view, model):
		self.view = view
		self.model = model
		statusbar = self.view.getParentViewWidget("statusbar")
		if statusbar["text"] == "No MasterNode Connection":
			self.view.errorLook()
		else:
			self.view.waitingLook()
			window = self.view.getWidget("window")
			window.update()
			connections = self.model.findConnections()
			self.view.connectionsLook(connections)
		self.set_events()
		
	
	def set_events(self):
		labels = self.view.getWidget("connections")
		for label in labels:
			label.bind("<Button-1>", self.select_connection)
		window = self.view.getWidget("widget_canvas")
		window.bind("<Key>", self.multiple)
		window.focus_set()
		select_button = self.view.getWidget("select_button")
		select_button["command"] = self.add_connections
	
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
		"""
		labels = []
		for i in range(15):
			labels.append(str(i))
		"""
		labels = self.view.getWidget("connections")
		names = []
		for label in labels:
			names.append(label["text"])
		main_view.add_connections(names)
		connections = main_view.getWidget("connections")
		
		for connection_name in connections:
			connection = connections[connection_name]
			self.model.addConnection(ConnectionController(connection,self.model))
			
		
		
		
	def __del__(self):
		labels = self.view.getWidget("connections")
		for label in labels:
			label.unbind(self.select_connection)
		
		window = self.view.getWidget("window")
		window.unbind(self.button_hold)

class ConnectionController:
	def __init__(self, view, model):
		self.view = view
		self.model = model
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
		main_view = self.view.getParentView()
		main_view.remove_connection(self.view.getName()) #gets destroyed when __del__ called anyway
		self.model.removeConnection(self.view.getName())
	
	def getViewName(self):
		return self.view.getName()
	
	def open_message_window(self):
		message_window = tk.Toplevel(self.view.getParentView().getWidget("window"))
		MessageController(MessageView(message_window, self.view.getName(), self.view.getParentView()), self.model)
		print("what is happening")
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
		self.__setEventBindings()
		self.receive = None
		self.send = None
		self.__run()
		
	
	def __run(self):
		#self.receive = threading.Thread(target = self.__getMessages)
		#self.receive.start()
		pass
		
	
	def __send_message(self):
		message_input = self.view.getWidget("entry")#"message_input")
		message = message_input.get("1.0",tk.END)
		message = message.strip()
		address = self.view.getName()
		print("address:" + address)
		address = address.strip()
		self.model.setSendingAddress(address)
		#for every new line add a \t
		self.model.incrementMessageNumber()
		self.model.load(message)
		self.__sending()
	
	def __sending(self):
		while not self.model.empty():
			window = self.view.getParentWidget("window")
			text_widget = self.view.getWidget("text_widget")
			number = self.model.getMessageNumber()
			text_widget.config(state="normal")
			entry = self.view.getWidget("entry")
			failed = False
		
			if self.model.send(): #and self.model.isFirstLine() need to adjust
				message = self.model.getMessageLastSent()
				#if self.model.sentFirstLine():
				text_widget.insert(tk.END, str(number) + "\t" + message + "\n")
				#	self.model.setSentFirstLine(False)
				#else:
					#text_widget.insert(tk.END, " " + "\t" + message + "\n")
				#	pass
			else:
				message = self.model.getMessageLastSent()
				#text_widget.insert(tk.END, str(number) + "\t" + message + "  FAILED\n")
				failed = True
			text_widget.config(state=tk.DISABLED)
		
			if failed:
				self.model.clearBuffer()
				self.model.setSentFirstLine(True)
				
			
			if self.model.sentLastLine():
				print("message last sent: ", self.model.getMessageLastSent())
				self.model.setSentLastLine(False)
				self.model.setSentFirstLine(True)
			#window.after(10, self.__sending)
		window.update()
		#else:
		print("tel me your secrets *******************")
		#self.send.join()
				
	
	def __getMessages(self):
		while True:
			message = self.model.receivePersonalMessage()
			if message != None and "\\x" not in message and message != "" and message != "\n":
				text_widget = self.view.getWidget("text_widget")
				message = message.strip()
				self.model.incrementMessageNumber()
				number = self.model.getMessageNumber()
				text_widget.config(state="normal")
				text_widget.insert(tk.END, str(number) + "\t" + message + "\n")
				text_widget.config(state=tk.DISABLED)
			#window = self.view.getWidget("window")
			#window.after(50, self.__getMessages)
		
	
	def __clearTextWidget(self):
		self.model.resetMessageNumber()
		text_widget = self.view.getWidget("text_widget")
		text_widget.config(state="normal")
		text_widget.delete("1.0", tk.END)
		text_widget.config(state=tk.DISABLED)
	"""
	def __send_message_thread(self):
		self.send = threading.Thread(target = self.__send_message)
		self.send.start()
	"""
		
			
	
	
	def __setEventBindings(self):
		
		send_button = self.view.getWidget("send_button")
		send_button["command"] = self.__send_message
		
		clear_button = self.view.getWidget("clear_button")
		clear_button["command"] = self.__clearTextWidget
		
		window = self.view.getWidget("window")
	
	def __del__(self):
		self.receive.join()
		self.send.join()
		print("what is going on")
		
		
		
		
		
		
		
		
		
		
		
		
		
