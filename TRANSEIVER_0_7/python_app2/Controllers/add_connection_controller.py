import tkinter as tk
from view_collection import SettingsView, AddConnectionView, MessageView
from functools import partial
import threading
import glob


class AddConnectionController: 
	def __init__(controller,view, model):
		controller.view = view
		controller.model = model
		controller.set_events()
	
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
