import tkinter as tk
class MessageController:
	def __init__(self, view, model):
		self.view = view
		self.model = model
		self.__setEventBindings()
		self.__run()
		
	def __run(self):
		self.model.start_threads()
		window = self.view.getWidget("window")
		window.after(20, self.__get_new_status)
	
	def hide(self):
		window = self.view.getWidget("window")
		window.withdraw()
	

	def __send_message(self):
		message_input = self.view.getWidget("entry")#"message_input")
		message = message_input.get("1.0",tk.END)
		message = message.strip()
		node_list = self.view.getNodeList() #must load addresses as well onto model to make this affective
		addresses = []
		for node_name in node_list:
			var = node_list[node_name][0]
			if var.get() == 1:
				addresses.append(node_name)
				
		self.model.load(message, ["\x00!!"]) # just for now
		
	
	
	def __get_new_status(self):
		message = self.model.new_status()
		if message != None:
			text_widget = self.view.getWidget("text_widget")
			text_widget.config(state="normal")
			text_widget.insert(tk.END, message + "\n")
			text_widget.config(state=tk.DISABLED)
		window = self.view.getWidget("window")
		window.after(20, self.__get_new_status)
	
	
	def __clearTextWidget(self):
		text_widget = self.view.getWidget("text_widget")
		text_widget.config(state="normal")
		text_widget.delete("1.0", tk.END)
		text_widget.config(state=tk.DISABLED)
	
		
	def __setEventBindings(self):
		
		send_button = self.view.getWidget("send_button")
		send_button["command"] = self.__send_message
		
		clear_button = self.view.getWidget("clear_button")
		clear_button["command"] = self.__clearTextWidget
		
		window = self.view.getWidget("window")
		window.protocol('WM_DELETE_WINDOW', self.hide)