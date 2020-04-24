import glob
from ctypes import c_bool
import multiprocessing 
import serial 
import traceback
import transceiver_commands as c
import time

MESSAGE = 0
STATE = 1
SUCCESS = 2
ADDRESS = 3
FILELINE = 4

def main():
    ports = glob.glob("/dev/tty.wchusbserial*")
    if(len(ports) == 0):
    	print("no ports available, program ending")
    	exit()
    print(ports)
    choice = int(input("choose port to open (enter 0 to " + str(len(ports)- 1)  + "):"))
    serial_port_name = ports[choice]
    com_process = None
    process_on = None
    sending = None
    try:
    	process_on = multiprocessing.Value(c_bool, False)
    	sending = multiprocessing.Queue()
    	com_process = multiprocessing.Process(target = communication, args = (serial_port_name, 9600,sending,process_on))
    	com_process.start()
    	choice = input("choose a mode(1,2,3): ")
    	if choice == "1":
    		menu()
    		choice = input("Enter value (x will end the program): ")
    		while choice != "x":
    			process_choice(choice, sending)
    			menu()
    			choice = input("Enter value: ")
    	elif choice == "2":
    		i = 0
    		while True:
    			if i < 255:
    				#sending.put(Command.personal_message(i,str(i),c.FINDING_ADDRESS)) #try file line
    				sending.put(Command.file_line(i,bytearray([i]),c.FINDING_ADDRESS)) #try file line
    				time.sleep(0.10) # i cant send it too fast
    				i = i + 1
    			else:
    				i = 0
    	elif choice == "3":
    		while True:
    			pass
		
    	
    
    except Exception as e:
    	print("hmmm:",e)
    	traceback.print_exc()
    finally:
    	process_on.value = False
    	for i in range(10):
    		pass
    	com_process.join()
    	sending.close()

def menu():
	print("1. get TX address\n" +\
		  "2. set TX address\n" +\
		  "3. get RX address\n" +\
		  "4. set RX address\n" +\
		  "5. address find\n")

def process_choice(choice, sending):
	if choice == "1":
		sending.put(Command.get_TX_address())
	elif choice == "2":
		address = input("enter new address: ")
		sending.put(Command.set_TX_address(address))
	elif choice == "3":
		pipe = int(input("Enter the address pipe: "))
		sending.put(Command.get_RX_address(pipe))
	elif choice == "4":
		pipe = int(input("Enter the address pipe: "))
		address = input("Enter the address: ")
		sending.put(Command.set_RX_address(pipe,address))
	elif choice == "5":
		sending.put(Command.address_return(c.FINDING_ADDRESS))
		


def communication(SERIAL_PORT_NAME, BAUD_RATE, sending, process_on):         #gets the receiving messages in a parallel process # this gets put under cases
	ser = None
	process_on.value = True
	try:
		ser = serial.Serial(SERIAL_PORT_NAME, BAUD_RATE, timeout = 0)
		while process_on.value:                   #maybe to improve reliability put them in seperate queues
			data = get_data(ser)		
			type = get_type(data)
			
			if type == MESSAGE:
				print("MESSAGE:", data[1:])
			elif type == STATE:
				print("STATE:", data[1:])
			elif type == SUCCESS:
				print("SUCCESS:",data[1:])
			elif type == ADDRESS:
				print("ADDRESS:", data[1:])
			elif type == FILELINE:
				print("FILELINE:",data[1:])
				
			
			if not sending.empty():
				bits = sending.get()
				print("BITSEND: ", bits)
				ser.write(bits)
				
	except Exception as e:
		print("ERROR: ", e)
	finally:
		ser.close()

def get_data(ser):
	data = bytearray()
	byte = ser.read()

	if len(byte) > 0:
		length = byte[0]
		i = 0
		while i < length:
			byte = ser.read()
			if len(byte) > 0:
				data.append(byte[0])
				i = i + 1
	return data

def get_type(data):
	type = None
	if len(data) > 0:
		type = data[0]
	return type
	


class CommandObject:
	def __init__(self):
		self.bits = bytearray(32)
	
	def set_USART_mode(self, mode):
		self.bits[0] = mode
	
	def get_bits(self):
		return bytes(self.bits)

class StateCommandObject(CommandObject):  #the way imma read the addresses in the arduino code different now
	
	def set_address_pipe(self, pipe):
		self.bits[1] = pipe
	
	def set_address(self, address):
		bit_index = 2
		for i in range(3):
			self.bits[bit_index] = address[i]
			bit_index += 1

class TransmitCommandObject(CommandObject):
	def set_WhenReceived_mode(self,mode):
		self.bits[1] = mode
		

class FindCommandObject(TransmitCommandObject):
	def set_source_address(self, address):
		bit_index = 2
		for i in range(3):
			self.bits[bit_index] = address[i]
			bit_index += 1
	

class MessageCommandObject(TransmitCommandObject):
	def set_message_id(self,ID):
		self.bits[2] = ID
	
	def set_message(self, message): #messages are now a length of 25
		if len(message) > c.MESSAGE_LENGTH:
			message = message[0:c.MESSAGE_LENGTH]
		bit_index = 3
		for i in range(len(message)):
			self.bits[bit_index] = message[i]
			bit_index += 1
	
	def set_source_address(self, address):
		bit_index = 29
		for i in range(3):
			self.bits[bit_index] = address[i]
			bit_index += 1
	
	
			
		

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

	

main()
