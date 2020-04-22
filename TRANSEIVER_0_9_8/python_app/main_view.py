import tkinter as tk
from message_view import MessageView
from connection_view import ConnectionView
from add_connection_view import AddConnectionView
from settings_view import SettingsView

class MainView:
	def __init__(self, parent):
		parent.title("main window")
		parent.geometry("360x500")
		parent.resizable(0,0)
		self.widgets = dict()
		self.widgets["window"] = parent
		self.connection_canvas_created = False
		self.connection_canvas_hiding = False
		
		self.connectionViews = dict()
		self.settingsView = SettingsView(tk.Toplevel(parent))
		self.addConnectionView = AddConnectionView(tk.Toplevel(parent))
		self.messageView = MessageView(tk.Toplevel(parent)) #xhiding it
		#maybe just make it automatically hide within the view class
		
	def getWidget(self, widget_name):
		return self.widgets[widget_name]
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
	def setConnectionView(self,view):
		self.connectionView = view
	
	def getConnectionViews(self):
		return self.connectionViews
	
	def setSettingsView(self,view):
		self.settingsView = view
	
	def getSettingsView(self):
		return self.settingsView
	
	def setAddConnectionView(self, view):
		self.addConnectionView = view
	
	def getAddConnectionView(self):
		return self.addConnectionView
		
	def setMessageView(self, view):
		self.messageView = view
	
	def getMessageView(self):
		return self.messageView
	
	def construct_view(self):
		window = self.widgets["window"]
		self.constructMenuBar(window)
		self.constructNoConnectionLabel(window)
		self.constructStatusBar(window)
	
	def constructMenuBar(self, window):
		menu = tk.Menu(window)
		self.widgets["Toolbar_menu"] = menu
		window.config(menu = menu)
		submenu = tk.Menu(menu)
		self.widgets["Application_dropmenu"] = submenu
		menu.add_cascade(label = "Application", menu = submenu)
		submenu.add_command(label = "Settings")
		submenu.add_command(label = "Add Connection")
	
	def constructNoConnectionLabel(self,window):
		frame = tk.Frame(window)
		self.widgets["connections_frame"] = frame
		
		label = tk.Label(frame, text = "No connections")
		self.widgets["no_connections_label"] = label
		
		label.pack(expand = True, fill = "both")
		frame.pack(expand = True, fill = "both")
	
	def hideNoConnectionLabel(self):
		label = self.widgets["no_connections_label"]
		if label.winfo_viewable():
			label.pack_forget()
		
	def showNoConnectionLabel(self):
		label = self.widgets["no_connections_label"]
		label.deiconify()
		
	def constructStatusBar(self, window):
		statusbar = tk.Label(window, text="No MasterNode Connection", bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.widgets["statusbar"] = statusbar
		statusbar.pack(side=tk.BOTTOM, fill=tk.X)
	
	def construct_connection_frame(self):
			
		frame = self.widgets["connections_frame"]
		
		canvas = tk.Canvas(frame)
		self.widgets["connections_canvas"] = canvas
		
		scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
		self.widgets["connections_scroll"] = scroll_y
		
		widget_frame = tk.Frame(canvas)
		self.widgets["widget_frame"] = widget_frame
		
		canvas.create_window(0, 0, anchor='nw', window=widget_frame)
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), 
						 yscrollcommand=scroll_y.set)
						 
		#widget_frame.pack(fill='both', expand=True)
		canvas.pack(fill='both', expand=True, side='left')
		scroll_y.pack(fill='y', side='right')
	
	def add_connection(self, address):           #this needs to be made
		self.hideNoConnectionLabel()
			
		if not self.connection_canvas_created:
			self.construct_connection_frame()
			self.connection_canvas_created = True
		
		if self.connection_canvas_hiding:
			canvas = self.widgets["connections_canvas"]
			scroll_y = self.widgets["connections_scroll"]
			canvas.pack(fill='both', expand=True, side='left')
			scroll_y.pack(fill='y', side='right')
			
		
		
		
		widget_frame = self.widgets["widget_frame"]
		self.connectionViews[address] = ConnectionView(address,widget_frame)
		
		canvas = self.widgets["connections_canvas"]
		scroll_y = self.widgets["connections_scroll"]
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)
		
			
			
		
	
	def remove_connection(self, address): #need to fix this
		if address not in self.connectionViews:
			return 
		connection = self.connectionViews[address]
		connection.destroy()
		del self.connectionViews[address]
		canvas = self.widgets["connections_canvas"]
		scroll_y = self.widgets["connections_scroll"]
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)
		
		if len(self.connectionViews) == 0:
			canvas.pack_forget()
			scroll_y.pack_forget()
			self.connection_canvas_hiding = True
			label = self.widgets["no_connections_label"]
			label.pack(expand = True, fill = "both")



		
		
		
		

	
		