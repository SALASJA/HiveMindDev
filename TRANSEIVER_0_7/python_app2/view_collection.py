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

class SettingsView:
	def __init__(self, toplevel_settings_window):
		self.widgets = dict()
		self.widgets["toplevel_settings_window"] = toplevel_settings_window
		toplevel_settings_window.title("Settings")
		toplevel_settings_window.geometry("400x400")
		toplevel_settings_window.withdraw()
		toplevel_settings_window.protocol('WM_DELETE_WINDOW', self.hide)
		self.main_view = None
		self.construct_view()
	
	def hide(self):
		toplevel_settings_window = self.widgets["toplevel_settings_window"]
		toplevel_settings_window.withdraw()
	
	def show(self):
		toplevel_settings_window = self.widgets["toplevel_settings_window"]
		toplevel_settings_window.deiconify()
	
	def getWidget(self, widget_name):
		return self.widgets[widget_name]
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
	def setMainView(self,main_view):
		self.main_view = main_view
	
	def getMainViewWidget(self,name):
		return self.main_view.getWidget(name)
		
	def construct_view(self):
		toplevel_settings_window = self.widgets["toplevel_settings_window"]
		tab_parent = ttk.Notebook(toplevel_settings_window)
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
		
		
		
	
	
	


class ConnectionView:
	def __init__(self, name, parent):
		self.name = name
		self.main_view = None
		self.widgets = dict()
		self.widgets["parent"] = parent
	
	def setMainView(self, main_view):
		self.main_view = main_view
		
	
	def getWidget(self, widget_name):
		return self.widgets[widget_name]
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
	def getParentWidget(self, widget_name):
		return self.main_view.getWidget(widget_name)
	
	def getMainView(self):
		return self.main_view
	
	def setMainView(self, main_view):
		self.main_view = main_view
	
	def getName(self):
		return self.name
	
	def constructLook(self):
		parent = self.widgets["parent"]
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
	
	
	def destroy(self):
		widgets = list(self.widgets.keys())
		for widget in widgets:
			#try:
			if widget != "parent" and widget != "image":
				self.widgets[widget].pack_forget()
				self.widgets[widget].destroy()
				del self.widgets[widget]
			#except Exception as e:
			#	print("Exception:",e)
			#	pass

class MessageView:
	def __init__(self, window, name = None, main_view = None):
		self.main_view = main_view
		self.name = name
		self.widgets = {}
		self.node_list = dict()
		self.widgets["window"] = window
		window.resizable(0,0)
		window.title(name)
		window.withdraw()
		#window.protocol('WM_DELETE_WINDOW', self.hide)
		self.construct_look()
	
	def hide(self):
		window = self.widgets["window"]
		window.withdraw()
	
	def show(self):
		window = self.widgets["window"]
		window.deiconify()	
		
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
	def getWidget(self, widget):
		return self.widgets[widget]
	
	def getParentWidget(self, widget):
		return self.main_view.getWidget(widget)
	
	def setMainView(self,main_view):
		self.main_view = main_view
	
	def getNodeList(self):
		return self.node_list
	
	def getWidget(self, name):
		return self.widgets[name]
	
	def getName(self):
		return self.name
	
	def construct_look(self):
		window = self.widgets["window"]
		self.__constructNodeListFrame(window)
		self.__constructMessageFrame(window)
	
	def __constructNodeListFrame(self,window):
		frame = tk.Frame(window)
		
		canvas = tk.Canvas(frame, width = 50)
		self.widgets["list_canvas"] = canvas
		
		scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
		self.widgets["list_scroll"] = scroll_y
		
		list_frame = tk.Frame(canvas)
		self.widgets["list_frame"] = list_frame
		
		canvas.create_window(0, 0, anchor='nw', window=list_frame)
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), 
						 yscrollcommand=scroll_y.set)
						 
		#widget_frame.pack(fill='both', expand=True)
		canvas.pack(fill='both', expand=True, side='left')
		scroll_y.pack(fill='y', side='right')
		frame.pack(fill='both', expand=True, side='left')
	
	def __constructMessageFrame(self, window):
		messaging_area_frame = tk.Frame(window)
		self.widgets["messaging_area_frame"] = messaging_area_frame
		self.__constructTextAreaFrame(messaging_area_frame)
		self.__constructTextInputFrame(messaging_area_frame)
		messaging_area_frame.pack(fill='both', expand=True, side='left')
		
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
	
	def add_node_to_list(self,address):
		list_frame = self.widgets["list_frame"]
		var = tk.IntVar()
		check_button = tk.Checkbutton(list_frame, text = address,  variable = var)
		check_button.pack()
		self.node_list[address] = [var,check_button]
		canvas = self.widgets["list_canvas"]
		scroll_y = self.widgets["list_scroll"]
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)
		
	
	def remove_node_from_list(self, address):
		if address in self.node_list:
			item = self.node_list[address]
			var = item[0]
			check_button = item[1]
			check_button.pack_forget()
			check_button.destroy()
			del self.node_list[address]
			canvas = self.widgets["list_canvas"]
			scroll_y = self.widgets["list_scroll"]
			canvas.update_idletasks()
			canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)
			
	
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
	
	
		
