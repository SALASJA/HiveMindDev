import serial
import glob
import io
import time
import multiprocessing
import curses
from tkinter import *
import tkinter.ttk as ttk


#ports = glob.glob("/dev/tty.wchusbserial*")[0]
#all_ports =  glob.glob("/dev/tty.wchusbserial*")
#print(all_ports)
# this port address is for the serial tx/rx pins on the GPIO header
#SERIAL_PORT = ports
# be sure to set this to the same rate used on the Arduino

PORT_STRING = "/dev/tty.wchusbserial*"
SERIAL_RATE = 9600
CLOSABLE = {}
OPEN_PROCESSES = {}
REGULAR_MESSAGING = 0  #because of the menu this is redundant for now but that will change
SET_TX_ADDRESS = 1
SET_RX_ADDRESS = 2
GET_TX_ADDRESS = 3
GET_RX_ADDRESS = 4

def receivingMessages(serial_port, queue):
	cant_decode = False
	while True:
		reading = serial_port.readline()
		try:
			string = reading.decode("utf-8")
		except:
			cant_decode = True
		if cant_decode or string[0:9] == "RECEIVED:" or string[0:8] == "ADDRESS:" or string[0:6] == "STATE:" or \
		    string[0:8] == "SUCCESS:":
		    reading = str(reading)
		    #reading = reading[2:len(reading) - 1]
		    #reading = reading.strip()
		    queue.put(reading) #had bytes in here directly before, the reading variable
	
		
class Messaging:
	def __init__(self):
		self.serialPort = None
		self.receiving = None
		self.receive_queue = None
		self.hasNotSent = True
		self.message_number = 0
		self.to_verify = []
		
	def closeSerialPort(self):
		if self.serialPort != None:
			self.receiving.join()
			self.serialPort.close()
			del OPEN_PROCESSES["serial_port"]
	
	def openSerialPort(self, serial_port_name):
		self.serialPort = serial.Serial(serial_port_name, SERIAL_RATE)
		CLOSABLE["serial_port"] = self.serialPort
		self.__setupProcesses()
	
	def __setupProcesses(self):
		self.receive_queue = multiprocessing.Queue()
		CLOSABLE["QUEUE"] = self.receive_queue
		self.receiving = multiprocessing.Process(target = receivingMessages, args = (self.serialPort, self.receive_queue))
		OPEN_PROCESSES["receiving"] = self.receiving
		self.receiving.start()
	
	def resetMessageNumber(self):
		self.message_number = 0
	
	def incrementMessageNumber(self):
		self.message_number += 1
	
	def getMessageNumber(self):
		return self.message_number
		
	def receiveMessage(self):
		message = None
		if self.receive_queue != None and not self.receive_queue.empty():
			message = self.receive_queue.get()
			if "ADDRESS:" in message:
				return message
			print(message)
			l = message.index(':') + 1                     #may need to remove this since its redundant now, has a part to process the address coming in
			if "\\x" in message:
				message = message[l:len(message) - 3]
			else:
				r = message.index('\\')
				message = message[l:r]
		return message
		
	
	def sendMessage(self, message):
		message = bytes(message + "\r", encoding ='utf-8')
		self.serialPort.write(message)
		
		
		
		
class Controller:
	def __init__(self, view, model = None):
		self.view = view
		self.model = model
		self.view.construct_look()
		self.__setEventBindings()
		self.__run()
	
	def __run(self):
		window = self.view.getWidget("window")
		window.after(50, self.__getMessages)
		
	
	def __usePort(self):
		self.model.closeSerialPort()
		label = self.view.getWidget("port_in_use_label")
		port_choice = self.view.getWidget("port_choice")
		serial_port_name = port_choice.get()
		label["text"] = serial_port_name
		if serial_port_name != "None selected":
			self.model.openSerialPort(serial_port_name)
			self.model.sendMessage(GET_TX_ADDRESS) #having an object oriented model would make this better
			time.sleep(0.5)
			self.model.sendMessage(GET_RX_ADDRESS)
			time.sleep(0.5)
			
	
	def __updatePortList(self):
		serialPortOptionMenu = self.view.getWidget("serialPortOptionMenu")
		port_choice = self.view.getWidget("port_choice")
		serial_ports = glob.glob(PORT_STRING)
		if len(serial_ports) == 0:
			self.model.closeSerialPort()
		menu = serialPortOptionMenu.children['menu']
		menu.delete(0,END)
		serial_ports.insert(0, "None selected")
		for val in serial_ports:
			menu.add_command(label=val,command=lambda v=port_choice,l=val:v.set(l))
		port_choice.set(serial_ports[0])
	
	def __send_message(self):
		mode = self.view.getWidget("mode")
		modes_dict = self.view.getWidget("modes_dict")
		mode_number = modes_dict[mode.get()]
		print(mode_number)
		message_input = self.view.getWidget("message_input")
		message = message_input.get()
		self.model.incrementMessageNumber()
		text_widget = self.view.getWidget("text_widget")
		number = self.model.getMessageNumber()
		text_widget.config(state="normal")
		text_widget.insert(END, str(number) + "\t" + message + "\n")
		text_widget.config(state=DISABLED)
		self.model.sendMessage(mode_number + message)
	
	def __getMessages(self):
		message = self.model.receiveMessage()
		if message != None and "ADDRESS:" not in message:
			text_widget = self.view.getWidget("text_widget")
			message = message.strip()
			self.model.incrementMessageNumber()
			number = self.model.getMessageNumber()
			text_widget.config(state="normal")
			text_widget.insert(END, str(number) + "\t" + message + "\n")
			text_widget.config(state=DISABLED)
		else:
			l = message.index(':') + 1
			if "\\x" in message:
				message = message[l:len(message) - 3]  ################################PROBLEM HERE AT THIS POINYT WE NEED AN OBJECT ORIENTED MODEL OF THE TRANSEIVER
			else:
				r = message.index('\\')
				message = message[l:r]
			tx_address_label = "example"
			
			
		window = self.view.getWidget("window")
		window.after(50, self.__getMessages)
	
	def __clearTextWidget(self):
		self.model.resetMessageNumber()
		text_widget = self.view.getWidget("text_widget")
		text_widget.config(state="normal")
		text_widget.delete("1.0", END)
		text_widget.config(state=DISABLED)
			
	
	
	def __setEventBindings(self):
		port_refresh_button = self.view.getWidget("port_refresh_button")
		port_refresh_button["command"] = self.__updatePortList
		
		port_select_button = self.view.getWidget("port_select_button")
		port_select_button["command"] = self.__usePort
		
		send_button = self.view.getWidget("send_button")
		send_button["command"] = self.__send_message
		
		clear_button = self.view.getWidget("clear_button")
		clear_button["command"] = self.__clearTextWidget
		
		window = self.view.getWidget("window")
		
		
	
		
		
	


class GUI_View:
	def __init__(self):
		self.widgets = {}
	
	def addWidget(self, name, widget):
		self.widgets[name] = widget
	
	def getWidget(self, name):
		return self.widgets[name]
	
	def construct_look(self):
		window = self.widgets["window"]
		self.__constructSerialPortFrame(window)
		self.__constructMessageFrame(window)
		
	def __constructSerialPortFrame(self, window):
		serial_port_frame = Frame(window)
		self.widgets["serial_port_frame"] = serial_port_frame
		self.__constructSerialPortSelectFrame(serial_port_frame)
		self.__constructPortInUseFrame(serial_port_frame)
		serial_port_frame.pack()
	
	def __constructSerialPortSelectFrame(self, serial_port_frame):
		serial_port_select_frame = Frame(serial_port_frame)
		self.widgets["serial_port_select_frame"] = serial_port_select_frame
		self.__constructSerialPortOptionMenu(serial_port_select_frame)
		self.__constructPortListRefreshButton(serial_port_select_frame)
		self.__constructPortSelectButton(serial_port_select_frame)
		serial_port_select_frame.pack()
	
	def __constructPortInUseFrame(self, serial_port_frame):
		serial_port_in_use_frame = Frame(serial_port_frame)
		self.widgets["serial_port_in_use_frame"] = serial_port_in_use_frame
		self.__constructPortInUseLabel(serial_port_in_use_frame)
		serial_port_in_use_frame.pack()
		
		
	
	def __constructSerialPortOptionMenu(self, serial_port_select_frame):
		serial_ports = glob.glob(PORT_STRING)
		port_choice = StringVar()
		serial_ports.insert(0,"None selected")
		self.widgets["port_choice"] = port_choice
		port_choice.set(serial_ports[0]) # default value
		serialPortOptionMenu = OptionMenu(serial_port_select_frame, port_choice, *serial_ports)
		self.widgets["serialPortOptionMenu"] = serialPortOptionMenu
		serialPortOptionMenu.pack(side = LEFT)
		
	def __constructPortListRefreshButton(self, serial_port_select_frame):
		port_refresh_button = Button(serial_port_select_frame, text = "Refresh")
		self.widgets["port_refresh_button"] = port_refresh_button
		port_refresh_button.pack(side = LEFT)
			
	def __constructPortSelectButton(self, serial_port_select_frame):
		port_select_button = Button(serial_port_select_frame, text = "Select")
		self.widgets["port_select_button"] = port_select_button
		port_select_button.pack(side = LEFT)	
	
	def __constructPortInUseLabel(self, serial_port_in_use_frame):
		port_in_use_label = Label(serial_port_in_use_frame, text = "None Selected")
		self.widgets["port_in_use_label"] = port_in_use_label
		port_in_use_label.pack(side = BOTTOM)
	
	
	def __constructMessageFrame(self, window):
		messaging_area_frame = Frame(window)
		self.widgets["messaging_area_frame"] = messaging_area_frame
		self.__constructTranseiverModeFrame(messaging_area_frame)
		self.__constructTextAreaFrame(messaging_area_frame)
		self.__constructTextInputFrame(messaging_area_frame)
		messaging_area_frame.pack()
	
	def __constructTranseiverModeFrame(self, messaging_area_frame):
		transeiver_mode_frame = Frame(messaging_area_frame)
		self.widgets["transeiver_mode_frame"] = transeiver_mode_frame
		self.__constructTranseiverModeOptionsFrame(transeiver_mode_frame)
		self.__constructTXAddressFrame(transeiver_mode_frame)
		self.__constructRXAddressFrame(transeiver_mode_frame)
		self.__constructAddressWriteButton(transeiver_mode_frame)
		transeiver_mode_frame.pack(side = TOP)
	
	def __constructTranseiverModeOptionsFrame(self, transeiver_mode_frame): # this will be repurposed
		mode_options_frame = Frame(transeiver_mode_frame)
		self.widgets["mode_options_frame"] = mode_options_frame
		modes = ['sending',\
		         'set Transmitting Address',\
		         'set Receiving Address',\
		         'get Transmitting Address',\
		         ' get Receiving Address']
		mode = StringVar()
		self.widgets["mode"] = mode
		modes_dict = {}
		i = 0
		for m in modes:
			modes_dict[m] = str(i)
			i = i + 1
		self.widgets["modes_dict"] = modes_dict
		mode.set(modes[0]) # default value
		transeiverModeOptionMenu = OptionMenu(mode_options_frame, mode, *modes)
		self.widgets["transeiverModeOptionMenu"] = transeiverModeOptionMenu
		transeiverModeOptionMenu.pack(side = TOP)
		mode_options_frame.pack(side = LEFT)
	
	def __constructTXAddressFrame(self,transeiver_mode_frame):
		tx_address_frame = Frame(transeiver_mode_frame)
		self.widgets["tx_address_frame"] = tx_address_frame
		self.__constructTXAddressEntry(tx_address_frame)
		self.__constructTXAddressLabel(tx_address_frame)
		tx_address_frame.pack(side = LEFT)
	
	def __constructTXAddressEntry(self,tx_address_frame):
		tx_address = StringVar()
		self.widgets["tx_address"] = tx_address
		tx_address_entry = Entry(tx_address_frame, textvariable = tx_address)
		self.widgets["tx_address_entry"] = tx_address_entry
		tx_address_entry.pack()
	
	def __constructTXAddressLabel(self,tx_address_frame):
		tx_address_label = Label(tx_address_frame, text = "TO:", anchor=W, justify=LEFT)
		self.widgets["tx_address_label"] = tx_address_label
		tx_address_label.pack(fill=X)

	def __constructRXAddressFrame(self,transeiver_mode_frame):
		rx_address_frame = Frame(transeiver_mode_frame)
		self.widgets["rx_address_frame"] = rx_address_frame
		self.__constructRXAddressEntry(rx_address_frame)
		self.__constructRXAddressLabel(rx_address_frame)
		rx_address_frame.pack(side = LEFT)

	def __constructRXAddressEntry(self,rx_address_frame):
		rx_address = StringVar()
		self.widgets["tx_address"] = rx_address
		rx_address_entry = Entry(rx_address_frame, textvariable = rx_address)
		self.widgets["tx_address_entry"] = rx_address_entry
		rx_address_entry.pack()
	
	def __constructRXAddressLabel(self,rx_address_frame):
		rx_address_label = Label(rx_address_frame, text = "FROM:", anchor=W, justify=LEFT)
		self.widgets["tx_address_label"] = rx_address_label
		rx_address_label.pack(fill=X)
	
	def __constructAddressWriteButton(self,transeiver_mode_frame):
		address_write_button = Button(transeiver_mode_frame, text = "set addresses")
		self.widgets["address_write_button"] = address_write_button
		address_write_button.pack(side = LEFT)
		
	def __constructTextAreaFrame(self, messaging_area_frame):
		text_frame = Frame(messaging_area_frame)
		self.widgets["text_frame"] = text_frame
		
		text_widget = Text(text_frame)
		self.widgets["text_widget"] = text_widget
		text_widget.config(state=DISABLED)
		
		scroll_bar = ttk.Scrollbar(text_frame, command = text_widget.yview)
		self.widgets["scroll_bar"] = scroll_bar
		text_widget["yscrollcommand"] = scroll_bar.set 
		
		text_widget.pack(side = LEFT)
		scroll_bar.pack(side = RIGHT, fill = Y)
		
		text_frame.pack()
	
	def __constructTextInputFrame(self,messaging_area_frame):
		input_frame = Frame(messaging_area_frame)
		self.widgets["input_frame"] = input_frame
		self.__constructEntry(input_frame)
		self.__constructSendButton(input_frame)
		self.__constructClearButton(input_frame)
		input_frame.pack()
	
	def __constructEntry(self, input_frame):
		message_input = StringVar()
		self.widgets["message_input"] = message_input
		entry = Entry(input_frame, textvariable = message_input)
		self.widgets["entry"] = entry
		entry.pack(side = LEFT)
		
	def __constructSendButton(self, input_frame):
		send_button = Button(input_frame, text = "send")
		self.widgets["send_button"] = send_button
		send_button.pack(side = LEFT)
	
	def __constructClearButton(self, input_frame):
		clear_button = Button(input_frame, text = "clear")
		self.widgets["clear_button"] = clear_button
		clear_button.pack(side = LEFT)
		 
	
class GUI:
	def __init__(self):
		window = Tk()
		view = GUI_View()
		view.addWidget("window", window)
		model = Messaging()
		Controller(view, model)
		window.mainloop()
		
		
def main():
	#try:
	GUI()
	"""
	except:
		pass
	finally:
		for closable in CLOSABLE:
			CLOSABLE[closable].close()
		for process in OPEN_PROCESSES:
			OPEN_PROCESSES[process].terminate()
	"""
	

if __name__ == "__main__":
	main()