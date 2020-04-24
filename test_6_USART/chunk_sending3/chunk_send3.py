import serial
import glob
import time
import multiprocessing
from ctypes import c_bool

def main():
	"""
	under my mac /dev/tty.wchusbserial1410 is the port
	* <--- uses of regular expressions in cases of more
	than one connection
	"""
	ports = glob.glob("/dev/tty.wchusbserial*") + glob.glob("/dev/tty.usbserial*") + glob.glob("COM3") + glob.glob("COM4")
	BAUDRATE = 9600
	choice = int(input((str(ports) + " enter numerical index for port: ")))
	portname = ports[choice]
	port = None
	sending_queue = None
	receiving_process_on = None
	receiving_process = None
	try:
		sending_queue = multiprocessing.Queue()
		receiving_process_on = multiprocessing.Value(c_bool,False)
		receiving_process = multiprocessing.Process(target = communication, args = (portname,BAUDRATE,sending_queue,receiving_process_on))
		receiving_process.start()
		while True:
			word = input("Enter a message: ")
			sending_queue.put(create_chunk(word)) #sending 32 bytes to the process queue
			
	except Exception as e:
		print("ERROR:", e)
	finally:
		receiving_process_on.value = False
		for i in range(10):   #wait for the process to stop
			pass
		if receiving_process != None:
			receiving_process.join()
		
		if sending_queue != None:
			sending_queue.close()
		

def communication(portname,BAUDRATE,sending_queue,receiving_process_on):
	receiving_process_on.value = True
	port = None
	try:
		port = serial.Serial(portname, BAUDRATE, timeout = 0)
		while receiving_process_on.value:
			bytelist = get_byte_group(port)
			if len(bytelist) > 0:
				print("Received Bytes: ", bytelist)
			
			if not sending_queue.empty():
				port.write(sending_queue.get())
				
	except Exception as e:
		print("Error: ", e)
	finally:
		if port != None:
			port.close()
"""
learned the hardway, but using a function to manually put in the bytes 
is the most reliable, safest method when creating a chunk of 32 bytes and instantly prevents
overshooting/undershooting the number of bytes. A bad method would involve using more creative and python methods
bad example : bytearray(bytes(word, encoding = "utf-8")) + bytearray(32 - len(word))
^^^^ this is unsafe and can lead to errors NEVER do this
"""
def create_chunk(word): 
	if len(word) > 32:
		word = word[0:32] #slice the string if its too long
	byteslist = bytearray(32) #making an array of bytes store 32 bytes
	for i in range(len(word)):
		byteslist[i] = ord(word[i]) #ord converts character to ascii value
	#print("byteslist: ",byteslist)
	return bytes(byteslist)         #turns the bytearray object back into a bytes object

def get_byte_group(port):
	byte = port.read()
	byteslist = bytearray()
	if len(byte) > 0:
		length = byte[0]
		i = 0
		while i < length:
			byte = port.read()
			if len(byte) > 0:
				byteslist.append(byte[0])
				i = i + 1
	return byteslist
	
	
main()