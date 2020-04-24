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
		byte = bytearray([1]) #can pass a byte array directly as well, this is the only way it can work
		while True:
			port.write(byte) #sending a 1 to microcontroller
			time.sleep(1) #waiting one second before sending again
			
	except Exception as e:
		print("ERROR:", e)
	finally:
		if port != None:
			port.close()
main()