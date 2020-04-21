import tkinter as tk
from main_controller import MainController
from master_transceiver_interface import MasterTransceiverInterface
from main_view import MainView

class Application:
	def __init__(self):
		window = tk.Tk()
		MainController(MainView(window),MasterTransceiverInterface())
		window.mainloop()