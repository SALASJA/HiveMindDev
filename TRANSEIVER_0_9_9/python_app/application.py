import tkinter as tk
from controllers.main_controller import MainController
from models.transceiver_interfaces.master_transceiver_interface import MasterTransceiverInterface
from views.main_view import MainView

class Application:
	def __init__(self):
		window = tk.Tk()
		MainController(MainView(window),MasterTransceiverInterface())
		window.mainloop()