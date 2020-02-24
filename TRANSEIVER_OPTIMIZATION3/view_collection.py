class View:
	def __init__(self, parent):
		parent.title("main window")
		parent.geometry("500x500")
		self.widgets = dict()
		self.widgets["window"] = parent
		self.construct_view()
	
	def construct_view(self):
		self.constructMenuBar()
	
	def constructMenuBar(self):
		window = self.widgets["window"]
		menu = tk.Menu(window)
		self.widgets["Application_menu"] = menu
		window.config(menu = menu)
		submenu = tk.Menu(menu)
		self.widgets["settings"] = submenu
		menu.add_cascade(label = "Application", menu = submenu)
		submenu.add_command(label = "Settings")
	
	def getWidget(self, widget_name):
		return self.widgets[widget_name]
		

class SettingsView:
	def __init__(self, parent):
		parent.title("Settings")
		parent.geometry("400x400")
		self.widgets = dict()
		self.widgets["window"] = parent
		self.construct_view()
	
	def construct_view(self):
		window = self.widgets["window"]
		tab_parent = ttk.Notebook(window, height = 300, width = 400)
		self.widgets["notebook"] = tab_parent
		
		self.construct_NRF24L01_settings_tab(tab_parent)
		
		tab_parent.pack(expand=1, fill='both')
		self.constructApplyButton(window)
		
		
		
	def construct_NRF24L01_settings_tab(self, tab_parent):
		tab1 = ttk.Frame(tab_parent)
		self.widgets["NRF24L01_settings_tab"] = tab1
		tab_parent.add(tab1, text="NRF24L01")
		
		canvas = tk.Canvas(tab1)
		self.widgets["NRF24L01_settings_canvas"] = canvas
		
		scroll_y = tk.Scrollbar(tab1, orient="vertical", command=canvas.yview)
		self.widgets["NRF24L01_settings_scroll"] = scroll_y
		
		widget_frame = tk.Frame(canvas)
		self.widgets["NRF24L01_settings_widget_frame"] = widget_frame

		self.construct_CONFIG_Register_Settings(widget_frame)
		self.construct_EN_AA_Register_Settings(widget_frame)
		self.construct_EN_RXADDR_Register_Settings(widget_frame)
		self.construct_SETUP_AW_Register_Settings(widget_frame)
		self.construct_SETUP_RETR_Register_Settings(widget_frame)
		self.construct_RF_CH_Register_Settings(widget_frame)
		self.construct_RF_SETUP_Register_Settings(widget_frame)
		self.construct_STATUS_Register_Settings(widget_frame)
		self.construct_OBSERVE_TX_Register_Settings(widget_frame)
		self.construct_RX_PW_PN_Registers_Settings(widget_frame)
		self.construct_FIFO_STATUS_Register_Settings(widget_frame)
		self.construct_DYNPD_Register_Settings(widget_frame)
			
			
		canvas.create_window(0, 0, anchor='nw', window=widget_frame)
		canvas.update_idletasks()
		canvas.configure(scrollregion=canvas.bbox('all'), 
						 yscrollcommand=scroll_y.set)
						 
		
		canvas.pack(fill='both', expand=True, side='left')
		scroll_y.pack(fill='y', side='right')
		
	def construct_CONFIG_Register_Settings(self, widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["CONFIG_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "CONFIG Register")
		self.widgets["CONFIG_label"] = config_label
		options = ["mask receiver interrupt",
		           "mask transmiter interrupt",
		           "mask max retransmits interrupt",
		           "Enable Cyclic Redundancy Check",
		           "CRC encoding scheme(unchecked 1 bit/checked 2 bits)"]
		
		config_label.pack()
		self.constructCheckButtonField(config_frame,options, 5, "CONFIG_bits", "CONFIG_checkbuttons")
		config_frame.pack(anchor = tk.W)
		
		
		
	def construct_EN_AA_Register_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["EN_AA_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "EN_AA Register")
		self.widgets["EN_AA_label"] = config_label
		options = ["Enable Auto Ack on data pipe 5",
				   "Enable Auto Ack on data pipe 4",
				   "Enable Auto Ack on data pipe 3",
				   "Enable Auto Ack on data pipe 2",
				   "Enable Auto Ack on data pipe 1",
				   "Enable Auto Ack on data pipe 0"]
		config_label.pack()
		self.constructCheckButtonField(config_frame,options, 6, "EN_AA_bits", "EN_AA_checkbuttons")
		config_frame.pack(anchor = tk.W)
		
	def construct_EN_RXADDR_Register_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["EN_RXADDR_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "EN_RXADDR Register")
		self.widgets["EN_RXADDR_label"] = config_label
		options = ["Enable data pipe 5",
				   "Enable data pipe 4",
				   "Enable data pipe 3",
				   "Enable data pipe 2",
				   "Enable data pipe 1",
				   "Enable data pipe 0"]
		config_label.pack()
		self.constructCheckButtonField(config_frame,options, 6, "EN_RXADDR_bits", "EN_RXADDR_checkbuttons")
		config_frame.pack(anchor = tk.W)
		
	def construct_SETUP_AW_Register_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["SETUP_AW_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "SETUP_AW Register")
		self.widgets["SETUP_AW_label"] = config_label
		options = ["3 byte address width",     #these should be radio buttons
				   "4 byte address width",
				   "5 byte address width"]
		config_label.pack()
		var = tk.IntVar()
		self.widgets["SETUP_AW_radio_var"] = var
		radiobuttons = []
		i = 0
		for option in options:
			radiobuttons.append(tk.Radiobutton(config_frame, text = option, variable = var, value = i))
			i = i + 1
		
		self.widgets["SETUP_AW_radiobuttons"] = radiobuttons
			
		for button in radiobuttons:
			button.pack(anchor = tk.W)
		config_frame.pack(anchor = tk.W)
		
	def construct_SETUP_RETR_Register_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["SETUP_RETR_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "SETUP_RETR Register")
		self.widgets["SETUP_RETR_label"] = config_label
		config_label.pack()
		
		label = tk.Label(config_frame, text = "Auto retransmit delay options")
		label.pack()
		options = []
		for i in range(16):
			options.append("Auto retransmit delay " +  str((i + 1) * 250) + " microseconds")
			
		var = tk.IntVar()
		self.widgets["SETUP_AW_radio_var"] = var
		radiobuttons = []
		i = 0
		for option in options:
			radiobuttons.append(tk.Radiobutton(config_frame, text = option, variable = var, value = i))
			i = i + 1
		
		self.widgets["SETUP_AW_radiobuttons"] = radiobuttons
			
		for button in radiobuttons:
			button.pack(anchor = tk.W)
		
		label = tk.Label(config_frame, text = "Auto retransmit count options")
		label.pack()
		options = ["Retransmit disabled"]
		for i in range(15):
			options.append("Up to " + str((i + 1)) + " retransmit on fail of Auto Ack ")
			
		var = tk.IntVar()
		self.widgets["SETUP_AW_radio_var"] = var
		radiobuttons = []
		i = 0
		for option in options:
			radiobuttons.append(tk.Radiobutton(config_frame, text = option, variable = var, value = i))
			i = i + 1
		
		self.widgets["SETUP_AW_radiobuttons"] = radiobuttons
			
		for button in radiobuttons:
			button.pack(anchor = tk.W)
		config_frame.pack(anchor = tk.W)
		
	def construct_RF_CH_Register_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["RF_CH_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "RF Channel Register")
		self.widgets["RF_CH_label"] = config_label
		
		var = tk.StringVar()
		config_label.pack()
		
		frame = tk.Frame(config_frame)
		entry = tk.Entry(frame, textvariable = var)
		label = tk.Label(frame, text = "configure a Channel from 0 - 128")
		entry.pack(side = "left")
		label.pack(side = "left")
		frame.pack(anchor = tk.W)
		config_frame.pack(anchor = tk.W)
		
	def construct_RF_SETUP_Register_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["EN_AA_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "EN_AA Register")
		self.widgets["EN_AA_label"] = config_label
			
		config_label.pack()
		self.constructCheckButtonField(config_frame,["hmmm"] * 8, 8, "EN_AA_bits", "EN_AA_checkbuttons")
		config_frame.pack()
		
		
	def construct_OBSERVE_TX_Register_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["EN_AA_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "EN_AA Register")
		self.widgets["EN_AA_label"] = config_label
			
		config_label.pack()
		self.constructCheckButtonField(config_frame,["hmmm"] * 8, 8, "EN_AA_bits", "EN_AA_checkbuttons")
		config_frame.pack()
		
	def construct_RX_PW_PN_Registers_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["EN_AA_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "EN_AA Register")
		self.widgets["EN_AA_label"] = config_label
			
		config_label.pack()
		self.constructCheckButtonField(config_frame,["hmmm"] * 8, 8, "EN_AA_bits", "EN_AA_checkbuttons")
		config_frame.pack()
		
	def construct_FIFO_STATUS_Register_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["EN_AA_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "EN_AA Register")
		self.widgets["EN_AA_label"] = config_label
			
		config_label.pack()
		self.constructCheckButtonField(config_frame,["hmmm"] * 8, 8, "EN_AA_bits", "EN_AA_checkbuttons")
		config_frame.pack()
		
	def construct_DYNPD_Register_Settings(self,widget_frame):
		config_frame = tk.Frame(widget_frame)
		self.widgets["EN_AA_frame"] = config_frame
		
		config_label = tk.Label(widget_frame, text = "EN_AA Register")
		self.widgets["EN_AA_label"] = config_label
			
		config_label.pack()
		self.constructCheckButtonField(config_frame,["hmmm"] * 8, 8, "EN_AA_bits", "EN_AA_checkbuttons")
		config_frame.pack()
	
	def constructApplyButton(self, settings_parent):
		button = tk.Button(settings_parent, text = "Apply")
		button.pack()
	
	def constructCheckButtonField(self, parent, labels, amount, bit_vars_groupname, checkbuttons_groupname):
		bit_vars = []
		checkbuttons = []
		for i in range(amount):
			v = tk.IntVar()
			bit_vars.append(v)
			checkbutton = tk.Checkbutton(parent, text = labels[i], variable = v)
			checkbuttons.append(checkbutton)
		
		self.widgets[bit_vars_groupname] = bit_vars
		self.widgets[checkbuttons_groupname] = checkbuttons
		
		for button in checkbuttons:
			button.pack(anchor = tk.W)