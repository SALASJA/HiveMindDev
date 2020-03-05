import tkinter as tk
from tkinter import ttk
import glob 
from PIL import Image, ImageTk

class MainView:
	def __init__(self, parent):
		parent.title("main window")
		parent.geometry("360x500")
		parent.resizable(0,0)
		self.widgets = dict()
		self.widgets["window"] = parent
		self.widgets["connections"] = dict()
		self.connection_frame_created = False
		self.connection_frame_hiding = False
	
	def getWidget(self, widget_name):
		return self.widgets[widget_name]
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
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
	
	def add_connections(self, addresses):           #this needs to be made
		if len(addresses) == 0:
			return 
			
		label = self.widgets["no_connections_label"]
		if label.winfo_viewable():
			label.pack_forget()
			
		if not self.connection_frame_created:
			self.construct_connection_frame()
			self.connection_frame_created= True
		
		if self.connection_frame_hiding:
			canvas = self.widgets["connections_canvas"]
			scroll_y = self.widgets["connections_scroll"]
			canvas.pack(fill='both', expand=True, side='left')
			scroll_y.pack(fill='y', side='right')
			
		
		
		
		connections = self.widgets["connections"]
		widget_frame = self.widgets["widget_frame"]
		filtered_addresses = []
		for address in addresses:
			if address not in connections:
				filtered_addresses.append(address)
				
		for address in filtered_addresses:
			connections[address] = ConnectionView(address, widget_frame,self)
		
		canvas = self.widgets["connections_canvas"]
		scroll_y = self.widgets["connections_scroll"]
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)
		
			
			
		
	
	def remove_connection(self, address): #need to fix this
		connections = self.widgets["connections"]
		connection = connections[address]
		#connection.destroy()
		del connections[address]
		canvas = self.widgets["connections_canvas"]
		scroll_y = self.widgets["connections_scroll"]
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)
		
		if len(connections) == 0:
			canvas.pack_forget()
			scroll_y.pack_forget()
			self.connection_frame_hiding = True
			label = self.widgets["no_connections_label"]
			label.pack(expand = True, fill = "both")
		
		
		
		
		
		
		
		
		
	
	
	


class ConnectionView:
	def __init__(self, name, parent, parent_view):
		self.name = name
		self.parent_view = parent_view
		self.widgets = dict()
		self.widgets["parent"] = parent
		self.constructLook(parent)
		
	
	def getWidget(self, widget_name):
		return self.widgets[widget_name]
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
	def getParentWidget(self, widget_name):
		return self.parent_view.getWidget(widget_name)
	
	def getParentView(self):
		return self.parent_view
	
	def getName(self):
		return self.name
	
	def constructLook(self,parent):
		window = self.getParentWidget("window")
		outerframe = tk.Frame(parent, bd = 2 , relief = tk.GROOVE, highlightbackground = "black")
		self.widgets["outerframe"] = outerframe
		
		self.constructExitFrame(outerframe)
		self.constructPictureFrame(outerframe)
		self.constructButtonFrame(outerframe)
		outerframe.pack()
	
	def constructExitFrame(self, outerframe):
		exitframe = tk.Frame(outerframe)
		self.widgets["exitframe"] = exitframe
		
		label = tk.Label(exitframe, text = self.name)
		self.widgets["label"] = label
		
		removebutton = tk.Button(exitframe, text = "x")
		self.widgets["removebutton"] = removebutton
		label.pack(side = "left")
		removebutton.pack(anchor = tk.E)
		exitframe.pack(fill = tk.X, expand = True)
	
	def constructPictureFrame(self,outerframe):
		pictureframe = tk.Frame(outerframe)
		self.widgets["pictureframe"] = tk.Frame(pictureframe)
		load = None 
		try:
			load = Image.open("python_app/image.gif")
		except:
			load = Image.open("image.gif")
		render = ImageTk.PhotoImage(load)
		img = tk.Label(pictureframe, image = render)
		img.image = render
		self.widgets["img"] = img
		self.widgets["image"] = render
		img.pack(anchor = tk.NW)
		pictureframe.pack()
	
	def constructButtonFrame(self, outerframe):
		buttonframe = tk.Frame(outerframe)
		self.widgets["buttonframe"] = buttonframe
		
		message_button = tk.Button(buttonframe, text = "message")
		self.widgets["message_button"] = message_button
		
		file_button = tk.Button(buttonframe, text = "send file")
		self.widgets["file_button"] = file_button
		
		data_button = tk.Button(buttonframe, text = "collect data")
		self.widgets["data_button"] = data_button
		
		settings_button = tk.Button(buttonframe, text = "settings")
		self.widgets["settings_button"] = settings_button
		message_button.pack(side = "left")
		file_button.pack(side = "left")
		data_button.pack(side = "left")
		settings_button.pack(side = "left")
		buttonframe.pack()
	
	"""
	def destroy(self):
		for widget in self.widgets:
			try:
				if widget != "parent":
					self.widgets[widget].pack_forget()
					self.widgets[widget].destroy()
					del widget[widget]
			except Exception as e:
				print("Exception:",e)
				pass
	"""
		
		
		
	

		
class SettingsView:
	def __init__(self, parent, main_view):
		self.widgets = dict()
		self.widgets["window"] = parent
		parent.title("Settings")
		parent.geometry("400x400")
		self.main_view = main_view
		self.construct_view()
	
	def getWidget(self, widget_name):
		return self.widgets[widget_name]
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
	def getParentViewWidget(self,name):
		return self.main_view.getWidget(name)
		
	def construct_view(self):
		window = self.widgets["window"]
		tab_parent = ttk.Notebook(window)
		self.widgets["notebook"] = tab_parent
		
		self.construct_SerialPort_Connection_settings_tab(tab_parent)
		
		tab_parent.pack(expand=1, fill='both')
		
		
		
	
	def construct_SerialPort_Connection_settings_tab(self, tab_parent):
		tab = ttk.Frame(tab_parent)
		self.widgets["Serial_port_connections_tab"] = tab
		tab_parent.add(tab, text="Serial port")
		self.__constructSerialPortFrame(tab)
		
	def __constructSerialPortFrame(self, tab):
		serial_port_frame = tk.Frame(tab)
		self.widgets["serial_port_frame"] = serial_port_frame
		self.__constructSerialPortSelectFrame(serial_port_frame)
		serial_port_frame.pack()
	
	def __constructSerialPortSelectFrame(self, serial_port_frame):
		serial_port_select_frame = tk.Frame(serial_port_frame)
		self.widgets["serial_port_select_frame"] = serial_port_select_frame
		self.__constructSerialPortOptionMenu(serial_port_select_frame)
		self.__constructPortListRefreshButton(serial_port_select_frame)
		self.__constructPortSelectButton(serial_port_select_frame)
		serial_port_select_frame.pack()
		
		
	
	def __constructSerialPortOptionMenu(self, serial_port_select_frame):
		serial_ports = glob.glob("/dev/tty.wchusbserial*") + glob.glob("/dev/tty.usbserial*") + glob.glob("COM5")
		port_choice = tk.StringVar()
		serial_ports.insert(0,"None selected")
		self.widgets["port_choice"] = port_choice
		port_choice.set(serial_ports[0]) # default value
		serialPortOptionMenu = tk.OptionMenu(serial_port_select_frame, port_choice, *serial_ports)
		self.widgets["serialPortOptionMenu"] = serialPortOptionMenu
		serialPortOptionMenu.pack(side = tk.LEFT)
		
	def __constructPortListRefreshButton(self, serial_port_select_frame):
		port_refresh_button = tk.Button(serial_port_select_frame, text = "Refresh")
		self.widgets["port_refresh_button"] = port_refresh_button
		port_refresh_button.pack(side = tk.LEFT)
			
	def __constructPortSelectButton(self, serial_port_select_frame):
		port_select_button = tk.Button(serial_port_select_frame, text = "Select")
		self.widgets["port_select_button"] = port_select_button
		port_select_button.pack(side = tk.LEFT)	
	
	def __constructPortInUseLabel(self, serial_port_in_use_frame):
		port_in_use_label = tk.Label(serial_port_in_use_frame, text = "None Selected")
		self.widgets["port_in_use_label"] = port_in_use_label
		port_in_use_label.pack(side = tk.BOTTOM)
		



class AddConnectionView:
	def __init__(self,parent, main_view):
		self.widgets = dict()
		self.widgets["window"] = parent
		parent.title("Available Connections")
		self.main_view = main_view
		parent.geometry("320x250")
		
	def getWidget(self, widget_name):
		return self.widgets[widget_name]
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
		
	def getParentViewWidget(self,name):
		return self.main_view.getWidget(name)
	
	def getMainView(self):
		return self.main_view
	
	def errorLook(self):
		window = self.widgets["window"]
		label = tk.Label(window, text = "No serial port selected")
		self.widgets["error_label"] = label
		label.pack(expand = True, fill = "both")
		
	
	def waitingLook(self):
		#if other widgets available deleted them
		window = self.widgets["window"]
		label = tk.Label(window, text = "Waiting...")
		self.widgets["waiting_label"] = label
		label.pack(expand = True, fill = "both")
	
	def connectionsLook(self, available_nodes = ["debugging"] * 20):
		self.widgets["waiting_label"].destroy()
		del self.widgets["waiting_label"]
		
		window = self.widgets["window"]
		frame = tk.Frame(window)
		canvas = tk.Canvas(frame)
		self.widgets["widget_canvas"] = canvas
		
		scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
		self.widgets["connections_scroll"] = scroll_y
		
		widget_frame = tk.Frame(canvas)
		self.widgets["connections_frame"] = widget_frame
		
		connections = []
		for node in available_nodes:
			label = tk.Label(widget_frame, text = node)
			connections.append(label)
			label.pack(anchor = tk.W)
		
		self.widgets["connections"] = connections
			
			
		canvas.create_window(0, 0, anchor='nw', window=widget_frame)
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), 
						 yscrollcommand=scroll_y.set)
		
						 
		
		canvas.pack(fill='both', expand=True, side='left')
		scroll_y.pack(fill='y', side='right')
		frame.pack(fill = 'x')
		button = tk.Button(window, text = "Add Selected")
		self.widgets["select_button"] = button
		button.pack(fill = 'both', expand = True)
		self.constructStatusBar(window)
		
	def constructStatusBar(self, window):
		statusbar = tk.Label(window, text="Single Node Selection Mode", bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.widgets["statusbar"] = statusbar
		statusbar.pack(side=tk.BOTTOM, fill=tk.X)	



class MessageView:
	def __init__(self, window, name, main_view):
		self.main_view = main_view
		self.name = name
		self.widgets = {}
		self.widgets["window"] = window
		window.resizable(0,0)
		window.title(name)
		self.construct_look()
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
	def getParentWidget(self, widget):
		return self.main_view.getWidget(widget)
	
	def getWidget(self, name):
		return self.widgets[name]
	
	def getName(self):
		return self.name
	
	def construct_look(self):
		window = self.widgets["window"]
		self.__constructMessageFrame(window)
	
	def __constructMessageFrame(self, window):
		messaging_area_frame = tk.Frame(window)
		self.widgets["messaging_area_frame"] = messaging_area_frame
		self.__constructTextAreaFrame(messaging_area_frame)
		self.__constructTextInputFrame(messaging_area_frame)
		messaging_area_frame.pack()
		
	def __constructTextAreaFrame(self, messaging_area_frame):
		text_frame = tk.Frame(messaging_area_frame)
		self.widgets["text_frame"] = text_frame
		
		text_widget = tk.Text(text_frame)
		self.widgets["text_widget"] = text_widget
		text_widget.config(state=tk.DISABLED)
		
		scroll_bar = ttk.Scrollbar(text_frame, command = text_widget.yview)
		self.widgets["scroll_bar"] = scroll_bar
		text_widget["yscrollcommand"] = scroll_bar.set 
		
		text_widget.pack(side = tk.LEFT)
		scroll_bar.pack(side = tk.RIGHT, fill = tk.Y)
		
		text_frame.pack()
	
	def __constructTextInputFrame(self,messaging_area_frame):
		input_frame = tk.Frame(messaging_area_frame)
		self.widgets["input_frame"] = input_frame
		self.__constructEntry(input_frame)
		self.__constructSendButton(input_frame)
		self.__constructClearButton(input_frame)
		input_frame.pack()
	
	def __constructEntry(self, input_frame):
		entry = tk.Text(input_frame, height = 3, width = 65)
		self.widgets["entry"] = entry
		entry.pack(side = tk.LEFT)
		
	def __constructSendButton(self, input_frame):
		send_button = tk.Button(input_frame, text = "send")
		self.widgets["send_button"] = send_button
		send_button.pack(side = tk.LEFT)
	
	def __constructClearButton(self, input_frame):
		clear_button = tk.Button(input_frame, text = "clear")
		self.widgets["clear_button"] = clear_button
		clear_button.pack(side = tk.LEFT)
	
	
		