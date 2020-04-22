from controllers.settings_controller import SettingsController
from controllers.add_connection_controller import AddConnectionController
class MainController:
	def __init__(self, view, model):
		self.view = view
		self.model = model
		self.view.construct_view()
		self.construct_subcontrollers()
		self.set_events()
	
	def construct_subcontrollers(self):
		settings_view = self.view.getSettingsView()
		settings_view.setMainView(self.view)
		SettingsController(settings_view, self.model)
		
	def set_events(self):
		dropmenu = self.view.getWidget("Application_dropmenu")
		dropmenu.entryconfig(0, command = self.open_settings)
		dropmenu.entryconfig(1, command = self.open_add_connection)
		window = self.view.getWidget("window")
		
	
	def open_settings(self):
		settings_view = self.view.getSettingsView()
		settings_view.show()
	
	def open_add_connection(self):
		add_connection_view = self.view.getAddConnectionView()
		add_connection_view.show() #refresh
		add_connection_view.setMainView(self.view)
		AddConnectionController(add_connection_view, self.model)
	
