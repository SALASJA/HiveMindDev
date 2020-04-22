import tkinter as tk
from tkinter import ttk
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