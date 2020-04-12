import serial
import glob
import time
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
	try:
		port = serial.Serial(portname, BAUDRATE, timeout = 0)
		while True:
			word = input("Enter a message: ")
			port.write(create_chunk(word)) #sending 32 bytes
			time.sleep(1) #waiting one second before sending again
			
	except Exception as e:
		print("ERROR:", e)
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
	return byteslist         #turns the bytearray object back into a bytes object
	
main()