import tkinter as tk
from controller_collection import MainController
from model_collection import MasterTransceiverInterface
from view_collection import MainView

class Application:
	def __init__(self):
		window = tk.Tk()
		MainController(MainView(window),MasterTransceiverInterface())
		window.mainloop()