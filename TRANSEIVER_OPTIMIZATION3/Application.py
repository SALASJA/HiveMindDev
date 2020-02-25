import tkinter as tk
from controller_collection import Controller
from model_collection import Transeiver
from view_collection import View

class Application:
	def __init__(self):
		window = tk.Tk()
		Controller(View(window),Transceiver())
		window.mainloop()