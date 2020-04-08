import tkinter as tk
from controller_collection import Controller
from model_collection import Network
from view_collection import MainView
import register_login as rl

class Application:
	def __init__(self):
                window = tk.Tk()
                Controller(MainView(window),Network())
                window.mainloop()
