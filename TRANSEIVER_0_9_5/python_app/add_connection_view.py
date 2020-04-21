import tkinter as tk
class AddConnectionView:
	def __init__(self,toplevel_add_connection_window):
		self.widgets = dict()
		self.widgets["toplevel_add_connection_window"] = toplevel_add_connection_window
		toplevel_add_connection_window.title("Available Connections")
		toplevel_add_connection_window.geometry("320x250")
		toplevel_add_connection_window.withdraw()
		toplevel_add_connection_window.protocol('WM_DELETE_WINDOW', self.hide)
		self.main_view = None
		self.connectionsLook()
	
	def hide(self):
		toplevel_add_connection_window = self.widgets["toplevel_add_connection_window"]
		toplevel_add_connection_window.withdraw()
		self.delete_connections()
	
	def delete_connections(self):
		canvas = self.widgets["widget_canvas"]
		connections = self.widgets["connections"]
		while len(connections) > 0:
			label = connections.pop()
			label.pack_forget()
			label.destroy()
		canvas.update()
		
	def show(self):
		toplevel_add_connection_window = self.widgets["toplevel_add_connection_window"]
		toplevel_add_connection_window.deiconify()
		
	def getWidget(self, widget_name):
		return self.widgets[widget_name]
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
	def setMainView(self, main_view):
		self.main_view = main_view
		
	def getParentViewWidget(self,name):
		return self.main_view.getWidget(name)
	
	def getMainView(self):
		return self.main_view

	
	def connectionsLook(self):
		toplevel_add_connection_window = self.widgets["toplevel_add_connection_window"]
		frame = tk.Frame(toplevel_add_connection_window)
		canvas = tk.Canvas(frame)
		self.widgets["widget_canvas"] = canvas
		
		scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
		self.widgets["connections_scroll"] = scroll_y
		
		widget_frame = tk.Frame(canvas)
		self.widgets["connections_frame"] = widget_frame
		
		
		self.widgets["connections"] = []
			
		canvas.create_window(0, 0, anchor='nw', window=widget_frame)
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), 
						 yscrollcommand=scroll_y.set)
		
						 
		
		canvas.pack(fill='both', expand=True, side='left')
		scroll_y.pack(fill='y', side='right')
		frame.pack(fill = 'x')
		button_frame = tk.Frame(toplevel_add_connection_window)
		
		select_button = tk.Button(button_frame, text = "Add Selected")
		self.widgets["select_button"] = select_button
		select_button.pack(fill = 'both', expand = True, side = "left")
		
		node_search_button = tk.Button(button_frame, text = "look for nodes")
		self.widgets["node_search_button"] = node_search_button
		node_search_button.pack(fill = 'both', expand = True, side = "left")
		button_frame.pack()
		self.constructStatusBar(toplevel_add_connection_window)
	
	def add_connections(self, available_nodes):
		self.delete_connections()
		widget_frame = self.widgets["connections_frame"]
		connections = self.widgets["connections"]
		canvas = self.widgets["widget_canvas"]
		for node in available_nodes:
			label = tk.Label(widget_frame, text = node)
			connections.append(label)
			label.pack(anchor = tk.W)
		canvas.update_idletasks()
		
	def constructStatusBar(self, toplevel_add_connection_window):
		statusbar = tk.Label(toplevel_add_connection_window, text="Single Node Selection Mode", bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.widgets["statusbar"] = statusbar
		statusbar.pack(side=tk.BOTTOM, fill=tk.X)	
