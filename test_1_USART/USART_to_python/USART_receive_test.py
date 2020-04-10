import serial
import glob

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
			byte = port.read()
			if len(byte) != 0: #successful transmission if positive bytes, must check because sometimes empty
				print("RECEIVED BYTE: ", byte)
	except Exception as e:
		print("ERROR:", e)
	finally:
		if port != None:
			port.close()
main()