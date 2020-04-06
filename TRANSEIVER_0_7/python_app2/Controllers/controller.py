import tkinter as tk
from view_collection import SettingsView, AddConnectionView, MessageView
from functools import partial
import threading
import glob


#Controller class for HiveMind
class Controller:
    def __init__(controller, view, model): #default controller initializing views, models, controllers
        controller.view = view
        controller.model = model
        controller.view.construct_view() # from view
        controller.create_subcontrollers() 
        controller.set_events()

    def create_subcontrollers(self):
        settings_view = self.view.getSettingsView()
        settings_view.setMainView(self.view)
        SettingsController(settings_view, self.model)

    def set_events(self):
        menu = self.view.getWidget("Application_dropmenu")
        menu.entryconfig(0, command = self.open_settings)
        menu.entryconfig(1, command = self.open_add_connection)
        window = self.view.getWidget("window")

    def open_settings(self):
        settings_view = self.view.getSettingsView()
        settings_view.show()

    def open_add_connection(self):
        add_connection_view = self.view.getAddConnectionView()
        add_connection_view.show()
        add_connection_view.setMainView(self.view)
        
        AddConnectionController(add_connection_view, self.model)

    def add_connection(self):
        add_connection_window = tk.Toplevel()
        add_connection_view = AddConnectionView(add_connection_window)

        self.view.setAddConnectionView(add_connection_view)
        add_connection_view.setMainView(self.view)

        AddConnectionController(add_connection_view, self.model)
        
