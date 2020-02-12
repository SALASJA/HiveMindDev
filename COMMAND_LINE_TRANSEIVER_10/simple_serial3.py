import serial
import glob
import multiprocessing

def main():
	greet()
	instructions()
	ser = None
	p1 = None
	receiving = None
	sending = None
	try:
		receiving = multiprocessing.Queue()
		sending = multiprocessing.Queue()
		port_name = getSerialPortName()
		p2 = multiprocessing.Process(target = printing, args = (receiving,))
		p1 = multiprocessing.Process(target = communication, args = (port_name, 9600, receiving, sending)) #running in parallel to main process this function, function processing in parallel
		p1.start()		#starts parallel process
		p2.start()
		while True:
			word = input("Enter a message to write:")  #gets user input
			sending.put(bytes(word + '\r', encoding = 'utf-8'))
	except Exception as e:
		print(e)
	finally:
		p1.terminate() #closes parallel process
		p2.terminate()
		receiving.close()
		sending.close()
		ser.close() #closes port

def getSerialPortName():   #handling exception handling of the port is also a good idea
	SERIAL_RATE = 9600
	ports = getAvailablePorts()
	print(ports)
	choice = int(input("choose port to open (enter index from 0 to " + str(len(ports) - 1)   + "):"))
	#need to add some code to prevent opening a port if its already in use
	SERIAL_PORT_NAME = ports[choice]
	#ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)
	return SERIAL_PORT_NAME

def communication(port_name, baud, receiving, sending):         #gets the receiving messages in a parallel process
	ser = None
	try:
		ser = serial.Serial(port_name, baud, timeout = 0)
		while True:
			reading = ser.readline()
			reading = str(reading)
			if reading != "b''":
				reading = format_received(reading)
				receiving.put(reading)
				print(not sending.empty())
			if(not sending.empty()):
				ser.write(sending.get())
	except Exception as e:
		print(e)
	finally:
		ser.close()

def printing(receiving):
	while True:
		if not receiving.empty():
			print("\r" + receiving.get())
			print("\nEnter a message to write:", end = '')



def format_received(reading):
	old_read = reading
	try:                                          #if you remove the try except and type clear, the INVALID state message will cause reading.index(':') to throw an exception
		l = reading.index(':') + 1
		if "\\x" in reading:
			reading = reading[l:len(reading) - 3]
		else:
			r = reading.index('\\')
			reading = reading[l:r]
	except:
		reading = old_read
	return reading
		
def getAvailablePorts():
	#ports = glob.glob("/dev/tty.wchusbserial*")  #gets a li
	ports = glob.glob("/dev/tty.usbserial*")
	while(len(ports) == 0):
		end = input("Enter 0 if you want to exit the program, otherwise plug in a board and enter a different value: ")
		if(end == '0'):
			exit()
		ports = glob.glob("/dev/tty.wchusbserial*")
	return ports

def greet():
	print("Welcome to the NRF24L01 Playground")

def instructions():
	print("preceeding 0 with input (ex. 0hello) will send hello")
	print("preceeding 1 with 5 characters following it will set the transmitting address (ex. 1abcde will set TXaddress to abcde")
	print("preceeding 2 with 5 characters following it will set the receiving address (ex. 2abcde will set RXaddress to abcde")
	print("preceeding 3 with any message (or just typing 3 by itself) returns the current transmitting address")
	print("preceeding 4 with any message (or just typing 4 by itself) returns the current receiving address")	
			
    	

if __name__ == "__main__":
	main()
