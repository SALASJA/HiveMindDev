import tkinter as tk
from view_collection import SettingsView, AddConnectionView, MessageView
from functools import partial
import threading
import glob

# Settings Controller class for HiveMind
class SettingsController:
    def __init__(controller, view, model):
            controller.view = view
            controller.model = model
            controller.set_events()

    def __usePort(self):
        self.model.closeSerialPort()
        label = self.view.getMainViewWidget("statusbar")
        port_choice = self.view.getWidget("port_choice")
        serial_port_name = port_choice.get()
        if serial_port_name != "None selected":
                label["text"] = "Connected on " + serial_port_name
                self.model.openSerialPort(serial_port_name)

    def __updatePortList(self):
            serialPortOptionMenu = self.view.getWidget("serialPortOptionMenu")
            port_choice = self.view.getWidget("port_choice")
            serial_ports = glob.glob("/dev/tty.wchusbserial*") + glob.glob("/dev/tty.usbserial*") + glob.glob("COM*")
            if len(serial_ports) == 0:
                    self.model.closeSerialPort()
            menu = serialPortOptionMenu.children["menu"]
            menu.delete(0, END)
            serial_ports.insert(0, "None selected")
            for val in serial_ports:
                    menu.add_command(label = val, command = lambda v = port_choice, 1 = val: v.set(1))
            port_choice.set(serial_ports[0])

    def set_events(self):
            port_refresh_button = self.view.getWidget("port_refresh_button")
	    port_refresh_button["command"] = self.__updatePortList
		
	    port_select_button = self.view.getWidget("port_select_button")
	    port_select_button["command"] = self.__usePort

	

