class Controller:
	def __init__(self, view, model):
		self.view = view
		self.model = model
		self.set_events()
	
	def set_events(self):
		settings = self.view.getWidget("settings")
		settings.entryconfig(0, command = self.settings)
	
	def settings(self):
		settings_window = tk.Toplevel()
		SettingsController(SettingsView(settings_window),self.model)


class SettingsController:
	def __init__(self,view, model):
		self.view = view
		self.model = model
		self.set_events()
		
	def set_events(self):
		pass
