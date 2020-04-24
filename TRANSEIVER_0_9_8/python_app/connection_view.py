import tkinter as tk
from PIL import Image, ImageTk
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
