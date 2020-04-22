import tkinter as tk
from tkinter import ttk
import glob 
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