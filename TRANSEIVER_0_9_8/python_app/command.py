from message_command_object import MessageCommandObject
from state_command_object import StateCommandObject
from find_command_object import FindCommandObject
import transceiver_commands as c 
class Command:
	@staticmethod
	def personal_message(ID, message, rx_address): #this might be easier to fix
		command = MessageCommandObject()
		command.set_USART_mode(c.TRANSMIT)
		command.set_WhenReceived_mode(c.PERSONAL_MESSAGE)
		command.set_message_id(ID)
		command.set_message(bytes(message, encoding = "utf-8"))
		command.set_source_address(bytes(rx_address, encoding = "utf-8"))
		return command.get_bits()
		
	@staticmethod
	def get_TX_address():
		command = StateCommandObject()
		command.set_USART_mode(c.GET_TX_ADDRESS)
		return command.get_bits()
	
	@staticmethod
	def set_TX_address(address):
		command = StateCommandObject()
		command.set_USART_mode(c.SET_TX_ADDRESS)
		command.set_address(bytes(address, encoding = "utf-8"))
		return command.get_bits()
	
	@staticmethod
	def get_RX_address(pipe):
		command = StateCommandObject()
		command.set_USART_mode(c.GET_RX_ADDRESS)
		command.set_address_pipe(pipe)
		return command.get_bits()
	
	@staticmethod
	def set_RX_address(pipe, address):
		command = StateCommandObject()
		command.set_USART_mode(c.SET_RX_ADDRESS)
		command.set_address_pipe(pipe)
		command.set_address(bytes(address, encoding = "utf-8"))
		return	command.get_bits()
	
	@staticmethod
	def address_return(return_address):
		command = FindCommandObject()
		command.set_USART_mode(c.TRANSMIT)
		command.set_WhenReceived_mode(c.ADDRESS_RETURN)
		command.set_source_address(bytes(return_address, encoding = "utf-8"))
		return command.get_bits()
	
	@staticmethod
	def file_line(ID,line,rx_address):#fix in case line is too small
		command = MessageCommandObject()
		command.set_USART_mode(c.TRANSMIT)
		command.set_WhenReceived_mode(c.FILE_LINE_SEND)
		command.set_message_id(ID)
		command.set_message(line)
		command.set_source_address(bytes(rx_address, encoding = "utf-8"))
		return command.get_bits()