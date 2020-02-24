import tkinter as tk
from view_collection import SettingsView, AddConnectionView
from functools import partial
import glob

class Controller:
	def __init__(self, view, model):
		self.view = view
		self.model = model
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
		serial_ports = glob.glob("/dev/tty.wchusbserial*")
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
		self.view.waitingLook()
		connections = self.model.findConnections()
		self.view.connectionsLook(connections)
		self.set_events()
	
	def set_events(self):
		labels = self.view.getWidget("connections")
		for label in labels:
			label.bind("<Button-1>", self.select_connection)
	
	def select_connection(self, event):
		labels = self.view.getWidget("connections")
		for label in labels:
			label["bg"] = "white"
			
		label = event.widget
		label["bg"] = "light blue"
		
	def __del__(self):
		labels = self.view.getWidget("connections")
		for label in labels:
			label.unbind("<Button-1>", self.select_connection)
		
		
		
		
		
		
		
		
		
		
		
		
