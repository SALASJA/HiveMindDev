import tkinter as tk
from view_collection import SettingsView, AddConnectionView, MessageView
from functools import partial
import threading
import glob

# Message Controller class for HiveMind
class MessageController:
	def __init__(controller, view, model):
		controller.view = view
		controller.model = model
		controller.send_thread = None #i create the threads in the module
		controller.receive_thread = None
		controller.lock = threading.Lock()
		controller.loop = False
		controller.__setEventBindings()
		controller.__run()
		
	
	def __run(self):
		self.receive_thread = threading.Thread(target = self.__getMessages, args = (self.lock,) )
		#self.receive_thread.setDaemon(True)
		self.receive_thread.start()
	
	def hide(self):
		window = self.view.getWidget("window")
		window.withdraw()
		if self.send_thread != None:
			self.send_thread.join()
		
		
	
	def __send_message(self, lock):
		message_input = self.view.getWidget("entry")#"message_input")
		message = message_input.get("1.0",tk.END)
		message = message.strip()
		addresses = self.view.getNodeList() #must load addresses as well onto model to make this affective      #set the address within the model i
		#self.__sending()
		text_widget = self.view.getWidget("text_widget")
		window = self.view.getWidget("window")
		for address in addresses:
			self.model.setSendingAddress(address)
			self.model.load(message)
			sent = self.model.send()
			while sent and not self.model.empty():
				sent = self.model.send()
		
		
		if not sent:
			message = self.model.getFailedMessage()
			lock.acquire()
			text_widget.config(state="normal")
			text_widget.insert(tk.END,message + "  FAILED\n")
			text_widget.config(state=tk.DISABLED)
			lock.release()
			self.model.setMessageLastSent("")
			return
	
		if self.model.empty():
			message = self.model.getMessageLastSent()
			lock.acquire()
			text_widget.config(state="normal")
			text_widget.insert(tk.END,message + "\n")
			text_widget.config(state=tk.DISABLED)
			lock.release()
			self.model.setMessageLastSent("")
		
	
	def __sending(self):
		text_widget = self.view.getWidget("text_widget")
		window = self.view.getWidget("window")
		sent = self.model.send()
		
		if not sent:
			text_widget.config(state="normal")
			message = self.model.getFailedMessage()
			text_widget.insert(tk.END,message + "  FAILED\n")
			text_widget.config(state=tk.DISABLED)
			self.model.setMessageLastSent("")
			return
		
		if not self.model.empty():   #here do something related to the addresses
			window.after(10, self.__sending)
		else:
			text_widget.config(state="normal")
			message = self.model.getMessageLastSent()
			text_widget.insert(tk.END,message + "\n")
			text_widget.config(state=tk.DISABLED)
			self.model.setMessageLastSent("")
			
			
				
	
	def __getMessages(self, lock):
		self.loop = True
		while self.loop:
			message = self.model.receive()
			if message != None:
				text_widget = self.view.getWidget("text_widget")
				lock.acquire()
				text_widget.config(state="normal")
				text_widget.insert(tk.END, message + "\n")
				text_widget.config(state=tk.DISABLED)
				lock.release()
		#window = self.view.getWidget("window")
		#window.after(10, self.__getMessages)
		
	
	def __clearTextWidget(self):
		self.model.resetMessageNumber()
		text_widget = self.view.getWidget("text_widget")
		self.lock.acquire()
		text_widget.config(state="normal")
		text_widget.delete("1.0", tk.END)
		text_widget.config(state=tk.DISABLED)
		self.lock.release()
	
	def __send_message_thread(self):
		if self.send_thread != None:
			self.send_thread.join()
		self.send_thread = threading.Thread(target = self.__send_message, args = (self.lock,))
		self.send_thread.start()
		
		
	def __setEventBindings(self):
		
		send_button = self.view.getWidget("send_button")
		send_button["command"] = self.__send_message_thread
		
		clear_button = self.view.getWidget("clear_button")
		clear_button["command"] = self.__clearTextWidget
		
		window = self.view.getWidget("window")
		window.protocol('WM_DELETE_WINDOW', self.hide)
	
	def __del__(self):
		self.loop = False
		if self.send_thread != None:
			print("close send thread")
			try:
				self.send_thread.join()
			except:
				pass
				
		if self.receive_thread != None:
			print("close receive thread")
			try:
				self.receive_thread.join()
			except:
				pass

		
		
		
		
		
		
		
		
		
		
		
		
		
